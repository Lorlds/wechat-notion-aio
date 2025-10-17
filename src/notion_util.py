from notion_client import Client
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, List, Optional, Any

class NotionHelper:
    def __init__(self, token: str):
        self.client = Client(auth=token)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    def query_db(self, database_id: str, **kwargs) -> Dict:
        return self.client.databases.query(database_id=database_id, **kwargs)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    def create_page(self, **kwargs) -> Dict:
        return self.client.pages.create(**kwargs)

    def rt(self, text: str) -> List[Dict]:
        return [{"type": "text", "text": {"content": (text or "")[:1800]}}]

    def title(self, text: str) -> List[Dict]:
        return [{"type": "text", "text": {"content": (text or '（无标题）')[:200]}}]

    def as_date(self, date_str: Optional[str]) -> Optional[Dict]:
        if not date_str:
            return None
        return {"start": date_str}

    # property builders
    def p_title(self, text: str) -> Dict: return {"title": self.title(text)}
    def p_rt(self, text: str) -> Dict: return {"rich_text": self.rt(text)}
    def p_url(self, url: Optional[str]) -> Dict: return {"url": url or None}
    def p_num(self, n: Optional[float]) -> Dict: return {"number": n if n is not None else None}
    def p_select(self, name: Optional[str]) -> Dict: return {"select": {"name": name} if name else None}
