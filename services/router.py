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

CHAT_STARTS = [
    "Harmonix",
    "Hey Harmonix",
    "Hello Harmonix",
    "Hi Harmonix",
    "Harmonix,",
    "Harmonix.",
    "Harmonix!",
]


async def classify(message: str) -> Intent:
    """
    Routes a user message into an intent.
    """

    heuristic = heuristic_route(message)
    print("Heuristic route:", heuristic)
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
    
    # Chat lookup

    if (
        any(lower.startswith(word.lower()) for word in CHAT_STARTS)
    ):
        return Intent.CHAT

    return None


async def llm_route(message: str) -> Intent:

    response = await chat(
        model="auto/best-reasoning",
        messages=[
            {
                "role": "system",
                "content": """
You are an intent classifier.

Return EXACTLY ONE of these labels.

TASK_CREATE
TASK_QUERY
NOTE_CREATE
NOTE_QUERY
CHAT

Definitions

TASK_CREATE
The user wants to create, remember, or save a task or todo.

TASK_QUERY
The user wants to view, search, ask about, or manage existing tasks.

NOTE_CREATE
The user wants to save information as a note.

NOTE_QUERY
The user wants to retrieve or search notes.

CHAT
Everything else.

Rules

- Return exactly one label.
- No explanations.
- No markdown.
- No punctuation.
- No extra words.

Examples

User: Buy milk tomorrow
TASK_CREATE

User: Finish CMSC machine problem Friday
TASK_CREATE

User: What are my tasks?
TASK_QUERY

User: What's due tomorrow?
TASK_QUERY

User: Save this note: SQLite supports JSON.
NOTE_CREATE

User: Show my notes.
NOTE_QUERY

User: How are you?
CHAT

User: What's the weather?
CHAT

User: Explain recursion.
CHAT
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    label = response["message"]["content"].strip().upper()
    VALID_INTENTS = {
        "TASK_CREATE",
        "TASK_QUERY",
        "NOTE_CREATE",
        "NOTE_QUERY",
        "CHAT"
    }

    raw = response["message"]["content"]

    intent = None

    for label in VALID_INTENTS:
        if label in raw:
            intent = label
            break

    if intent is None:
        intent = "CHAT"
    try:
        return Intent[label]

    except KeyError:
        return Intent.CHAT