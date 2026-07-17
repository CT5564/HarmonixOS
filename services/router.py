#Identifies the intent of a user message. Uses heuristics first, 
#then falls back to LLM if no heuristic matches.
#Actions are defined in the dispatcher, which is called by the router.

from enum import Enum

from services.ollama_client import chat


class Intent(Enum):
    TASK_CREATE = "TASK_CREATE"
    TASK_QUERY = "TASK_QUERY"

    NOTE_CREATE = "NOTE_CREATE"
    NOTE_QUERY = "NOTE_QUERY"

    CHAT = "CHAT"

    UNKNOWN = "UNKNOWN"


TASK_STARTS = [
    "buy",
    "finish",
    "submit",
    "call",
    "email",
    "pay",
    "schedule",
    "do",
    "complete",
    "fix",
]

TASK_QUERY_WORDS = [
    "today",
    "task",
    "tasks",
    "todo",
    "to-do",
    "schedule",
]

NOTE_STARTS = [
    "remember",
    "note",
    "idea",
]


async def classify(message: str) -> Intent:
    """
    Routes a user message into an intent.
    """

    heuristic = heuristic_route(message)

    if heuristic is not None:
        return heuristic

    return await llm_route(message)


def heuristic_route(message: str) -> Intent | None:

    lower = message.lower().strip()

    # Task creation

    if any(lower.startswith(word) for word in TASK_STARTS):
        return Intent.TASK_CREATE

    # Note creation

    if any(lower.startswith(word) for word in NOTE_STARTS):
        return Intent.NOTE_CREATE

    # Task lookup

    if (
        "what" in lower
        and any(word in lower for word in TASK_QUERY_WORDS)
    ):
        return Intent.TASK_QUERY

    return None


async def llm_route(message: str) -> Intent:

    response = await chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": """
You are an intent classifier.

Return ONLY one of the following labels.

TASK_CREATE
TASK_QUERY
NOTE_CREATE
NOTE_QUERY
CHAT

Do not explain.
Do not add punctuation.
Do not add any other text.
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    label = response["message"]["content"].strip().upper()

    try:
        return Intent[label]

    except KeyError:
        return Intent.CHAT