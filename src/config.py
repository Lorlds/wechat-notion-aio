import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_SOURCES_DB = os.getenv("NOTION_SOURCES_DB")
NOTION_EVENTS_DB = os.getenv("NOTION_DB_ID")
NOTION_RULES_DB = os.getenv("NOTION_RULES_DB")
NOTION_DAILY_PARENT = os.getenv("NOTION_DAILY_PARENT")

missing = [k for k,v in [
    ("NOTION_TOKEN", NOTION_TOKEN),
    ("NOTION_SOURCES_DB", NOTION_SOURCES_DB),
    ("NOTION_DB_ID", NOTION_EVENTS_DB),
    ("NOTION_RULES_DB", NOTION_RULES_DB),
    ("NOTION_DAILY_PARENT", NOTION_DAILY_PARENT),
] if not v]

if missing:
    raise SystemExit(f"Missing required environment variables: {missing}")
