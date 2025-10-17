import os, datetime, pytz
from typing import List, Dict
from notion_client import APIResponseError

from .config import NOTION_TOKEN, NOTION_SOURCES_DB, NOTION_EVENTS_DB, NOTION_RULES_DB, NOTION_DAILY_PARENT
from .notion_util import NotionHelper
from .rules import compile_rules, score_text
from .fetch import fetch_items, extract_deadline

def d_today():
    return datetime.datetime.now(pytz.timezone("Asia/Shanghai")).date().isoformat()

def load_enabled_sources(nh: NotionHelper) -> List[Dict]:
    rows = []
    start = None
    filt = {"filter": {"and": [
        {"property": "Enabled", "checkbox": {"equals": True}},
        {"property": "FeedURL", "url": {"is_not_empty": True}},
    ]}}
    while True:
        resp = nh.query_db(NOTION_SOURCES_DB, **({**filt, "start_cursor": start} if start else filt))
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"): break
        start = resp.get("next_cursor")
    out = []
    for r in rows:
        p = r["properties"]
        name = p["Name"]["title"][0]["plain_text"] if p["Name"]["title"] else "未命名源"
        url = p["FeedURL"]["url"]
        out.append({"name": name, "url": url})
    return out

def load_rules(nh: NotionHelper):
    rows = []
    start = None
    while True:
        resp = nh.query_db(NOTION_RULES_DB, start_cursor=start) if start else nh.query_db(NOTION_RULES_DB)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"): break
        start = resp.get("next_cursor")
    return compile_rules(rows)

def exists_link(nh: NotionHelper, link: str) -> bool:
    try:
        q = nh.query_db(NOTION_EVENTS_DB, filter={"property": "Link", "url": {"equals": link}})
        return len(q.get("results", [])) > 0
    except APIResponseError:
        return False

def create_event(nh: NotionHelper, item: Dict):
    props = {
        "Name": nh.p_title(item["title"]),
        "Type": nh.p_select(item.get("type")),
        "Source": nh.p_rt(item.get("source","")),
        "Published": {"date": nh.as_date(item.get("published"))},
        "Deadline": {"date": nh.as_date(item.get("deadline"))},
        "Score": nh.p_num(item.get("score")),
        "Link": nh.p_url(item.get("link")),
        "Summary": nh.p_rt(item.get("summary") or ""),
    }
    nh.create_page(parent={"database_id": NOTION_EVENTS_DB}, properties=props)

def create_daily(nh: NotionHelper, items: List[Dict], date_str: str):
    title = f"📅 {date_str} 竞赛/活动简报"
    if not items:
        children = [{"object":"block","type":"paragraph","paragraph":{"rich_text": nh.rt("今天没有达到阈值的条目。可以在 Rules 库调低最低分，或新增关键词。")}}]
    else:
        children = []
        for it in items:
            line = f"• {it['title']}（{it.get('type','?')}｜分 {it.get('score',0)}｜源 {it.get('source','')}）\\n{it.get('link','')}"
            children.append({"object":"block","type":"paragraph","paragraph":{"rich_text": nh.rt(line)}})
    nh.create_page(parent={"page_id": NOTION_DAILY_PARENT}, properties={"title": [{"type":"text","text":{"content": title}}]}, children=children)

def main():
    nh = NotionHelper(NOTION_TOKEN)
    rules, min_score = load_rules(nh)
    sources = load_enabled_sources(nh)
    picked = []

    for s in sources:
        for it in fetch_items(s["url"]):
            text = f"{it['title']}\\n{it.get('summary','')}\\n{it.get('raw','')}"
            score, typ, hard = score_text(text, rules)
            if hard:
                continue
            ddl = extract_deadline(text)
            if ddl:
                score += 2  # deadline bonus

            it["score"] = round(score, 2)
            it["type"] = typ or "活动"
            it["source"] = s["name"]
            it["deadline"] = ddl
            it["summary"] = (it.get("summary") or it.get("raw") or "")[:500]

            if it.get("link") and exists_link(nh, it["link"]):
                continue
            if it["score"] >= min_score:
                create_event(nh, it)
                picked.append(it)

    create_daily(nh, picked, d_today())

if __name__ == "__main__":
    main()
