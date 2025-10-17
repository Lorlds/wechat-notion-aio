import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class Rule:
    key: str
    pattern: Optional[str]
    weight: float
    hard_block: bool
    enabled: bool
    compiled: Optional[re.Pattern] = None

def compile_rules(rows: List[Dict]) -> Tuple[List[Rule], float]:
    rules: List[Rule] = []
    min_score = 3.0
    for row in rows:
        props = row.get("properties", {})
        key = props.get("Key", {}).get("select", {}).get("name")
        if not key:
            continue
        # text / rich_text 读取兼容
        pat = ""
        if "Pattern" in props:
            if props["Pattern"].get("rich_text"):
                pat = "".join(rt.get("plain_text","") for rt in props["Pattern"]["rich_text"])
            elif props["Pattern"].get("text"):
                pat = props["Pattern"]["text"]
        weight = props.get("Weight", {}).get("number")
        hard = bool(props.get("HardBlock", {}).get("checkbox", False))
        en = bool(props.get("Enabled", {}).get("checkbox", False))

        r = Rule(key=key, pattern=pat or None, weight=float(weight or 0), hard_block=hard, enabled=en)
        if r.pattern:
            try:
                r.compiled = re.compile(r.pattern, re.I | re.M)
            except re.error:
                r.enabled = False  # 坏正则自动禁用
        rules.append(r)

        if key == "MIN_SCORE" and weight is not None:
            min_score = float(weight)
    return rules, min_score

def score_text(text: str, rules: List[Rule]) -> Tuple[float, Optional[str], bool]:
    score = 0.0
    type_name = None
    hard_blocked = False
    for r in rules:
        if not r.enabled or not r.compiled:
            continue
        if r.compiled.search(text or ""):
            if r.hard_block:
                hard_blocked = True
            score += r.weight
            if r.key == "TRIGGERS_COMP":
                type_name = "竞赛"
            elif r.key == "TRIGGERS_EVENT" and type_name is None:
                type_name = "活动"
    return score, type_name, hard_blocked
