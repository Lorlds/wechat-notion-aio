import re, time, urllib.parse, requests, feedparser
from typing import Dict, Iterable, Optional
from bs4 import BeautifulSoup

UA = {"User-Agent": "wechat-notion-aio/1.0 (+github-actions)"}

def _clean(html_or_text: str) -> str:
    if not html_or_text:
        return ""
    soup = BeautifulSoup(html_or_text, "html.parser")
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\s+\n", "\n", text)
    return text

def extract_deadline(text: str) -> Optional[str]:
    if not text: return None
    m = re.search(r"(20\\d{2})[./-](\\d{1,2})[./-](\\d{1,2})", text)
    if m:
        y, m1, d = m.groups()
        return f"{y}-{m1.zfill(2)}-{d.zfill(2)}"
    m = re.search(r"(\\d{1,2})\\s*月\\s*(\\d{1,2})\\s*日", text)
    if m:
        import datetime
        y = datetime.date.today().year
        mo, d = m.groups()
        return f"{y}-{str(mo).zfill(2)}-{str(d).zfill(2)}"
    return None

def fetch_items(feed_url: str, timeout: int = 15) -> Iterable[Dict]:
    # Try RSS/Atom first
    try:
        parsed = feedparser.parse(feed_url)
        if getattr(parsed, "entries", None):
            for e in parsed.entries:
                title = e.get("title") or ""
                link = e.get("link") or ""
                summary = _clean(e.get("summary", ""))
                published = None
                for k in ("published_parsed", "updated_parsed", "created_parsed"):
                    if e.get(k):
                        tm = e.get(k)
                        published = time.strftime("%Y-%m-%d", tm)
                        break
                yield {"title": title, "link": link, "summary": summary, "published": published, "raw": summary}
            return
    except Exception:
        pass

    # Fallback: fetch page and parse anchors
    try:
        r = requests.get(feed_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a"):
            href = a.get("href") or ""
            text = (a.get_text() or "").strip()
            if not href or not text: 
                continue
            if "mp.weixin.qq.com" in href or href.startswith("http"):
                yield {"title": text[:180], "link": urllib.parse.urljoin(feed_url, href), "summary": "", "published": None, "raw": text}
    except Exception:
        return
