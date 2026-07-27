import json

from models.task import Task
from services.omniroute_client import chat

from services.log import get_log
from datetime import datetime

log = get_log(__name__)
from zoneinfo import ZoneInfo


def _get_today():
    return datetime.now(
        ZoneInfo("Asia/Manila")
    ).date()


SYSTEM_PROMPT = """
You extract task information.

Return ONLY valid JSON.
Today's date is {today}.

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
  You MUST always return a project from the list below.
  Match the user's message to the closest project.
  If no project is mentioned, pick the most likely one based on context (e.g. school-related tasks go to a school project, personal tasks go to Personal).
  Never return null for project.

- tags:
  Array of strings.

If the user does not explicitly specify:
- priority
- tags

return null (or [] for tags).

Do not guess priority or tags.

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

Possible Projects:

"""


async def extract_task(
    prompt: str,
    author_id: str,
    projects: list[str]
) -> Task:

    try:

        log.info(
            f"Extracting data for user: {author_id}"
        )
        PROJECT_LIST = "\n".join(
            f"- {project}"
            for project in projects
        )
        today = _get_today()
        response = await chat(
            model="auto/best-reasoning",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(today=today) + PROJECT_LIST
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        raw = (
            response[
                "message"
            ][
                "content"
            ].strip()
        )


        data = json.loads(
            raw
        )


        return Task(
            author_id=author_id,
            title=(
                data.get(
                    "title"
                )
                or prompt
            ),
            description=data.get(
                "description"
            ),
            due_date=data.get(
                "due_date"
            ),
            due_time=data.get(
                "due_time"
            ),
            priority=data.get(
                "priority"
            ),
            project=data.get(
                "project"
            ),
            tags=data.get(
                "tags",
                []
            )
        )


    except Exception as e:

        log.error(
            f"{e}"
        )


        # Fallback task must also
        # preserve the user ID.

        return Task(
            author_id=author_id,
            title=prompt
        )