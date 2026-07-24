import os

from dotenv import load_dotenv
from notion_client import Client


load_dotenv()


NOTION_TOKEN = os.getenv("NOTION_TOKEN")


if not NOTION_TOKEN:

    raise RuntimeError(
        "NOTION_TOKEN is not set in .env"
    )


notion = Client(
    auth=NOTION_TOKEN
)