import os
from dotenv import load_dotenv

load_dotenv()

DEV_CHANNEL = int(os.getenv("DEV_CHANNEL"))

NOTION_TASKS_DB_ID = "1d798e489e2b80f4aa4ccf3a01993734"
NOTION_PROJECTS_DB_ID = "12f98e489e2b81adb67ccdc6f51f0989"

NOTION_WEBHOOK_PORT = int(
    os.getenv("NOTION_WEBHOOK_PORT", "8080")
)
NOTION_WEBHOOK_SECRET = os.getenv(
    "NOTION_WEBHOOK_SECRET", ""
)
