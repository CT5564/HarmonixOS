import json
from datetime import date

from models.task import Task
from services.ollama_client import chat


SYSTEM_PROMPT = f"""
You extract task information.

Return ONLY valid JSON.

Rules:

- title:
    The actual task name.
    Do NOT include dates or times.

- description:
    Extra details only.
    If none, return null.

- due_date:
    Convert relative dates into YYYY-MM-DD.
    If user does not specify a date, return tomorrow's date.

- due_time:
    Convert to 24-hour HH:MM format.
    If user does not specify a time, return 23:59.

- priority:
    Only one of:
    low
    medium
    high
    or null.

- project:
    Return null if unknown.

- tags:
    Array of strings.

If the user does not explicitly specify:

- priority
- project
- tags

return null (or [] for tags).

Do not guess.

Return ONLY JSON.

Schema: 
{{
    "title": "",
    "description": "",
    "due_date": "",
    "due_time": "",
    "priority": "",
    "project": "",
    "tags": []
}}

DO NOT explain anything.
DO NOT wrap the JSON in markdown.
DO NOT include any extra text.
"""


async def extract_task(prompt: str) -> Task:

    try:
        print("Extracting data")
        response = await chat(
            model="auto/best-reasoning",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = response["message"]["content"].strip()

        data = json.loads(raw)

        return Task(
            title=data.get("title") or prompt,
            description=data.get("description"),
            due_date=data.get("due_date"),
            due_time=data.get("due_time"),
            priority=data.get("priority"),
            project=data.get("project"),
            tags=data.get("tags", [])
        )

    except Exception as e:

        print(f"[Entity Extractor] {e}")

        return Task(
            title=prompt
        )