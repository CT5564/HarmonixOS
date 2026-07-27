# Plan Agent
#
# Uses read-only tools to explore the codebase,
# then produces a structured plan. Agent decides
# what to read — no giant context dumps.

from services.omniroute_client import chat
from services.context import build_context
from agents.tools import TOOL_DEFINITIONS, execute_tool

MODEL = "auto/best-reasoning"

MAX_TOOL_ROUNDS = 10

# Read-only subset: no edit_file or create_file
PLAN_TOOLS = [
    t for t in TOOL_DEFINITIONS
    if t["function"]["name"] in (
        "search_code", "read_file", "finish"
    )
]

SYSTEM_PROMPT = """
You are Harmonix's planning agent.

You have read-only tools to explore the codebase before planning.
Use search_code and read_file to understand what exists.

Workflow:
1. search_code to find relevant files.
2. read_file to study the code.
3. Repeat until you understand the codebase.
4. finish with your plan as the summary.

Output format for your summary:

## Plan: [Task Title]

### Steps
1. **[File path]** — What to do
2. **[File path]** — What to do
...

### Files Affected
- `path/to/file.py` — reason
...

### Notes
- Risks, verification steps, dependencies
"""


async def plan_agent(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> str:
    """Produce a plan using tool-calling exploration."""

    user_context = ""
    if author_name:
        user_context = f"\n\nCURRENT USER: {author_name}"

    memory_context = await build_context(
        prompt,
        author_id=author_id,
        author_name=author_name
    )

    messages = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + user_context
                + (
                    f"\n\n## Memory Context\n\n{memory_context}"
                    if memory_context
                    else ""
                )
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    for round_num in range(MAX_TOOL_ROUNDS):

        response = await chat(
            model=MODEL,
            messages=messages,
            tools=PLAN_TOOLS
        )

        assistant_msg = response["message"]
        messages.append(assistant_msg)

        if not assistant_msg.get("tool_calls"):
            break

        for tool_call in assistant_msg["tool_calls"]:

            tc_id = tool_call["id"]
            func_name = tool_call["function"]["name"]

            try:
                import json as _json
                args = _json.loads(
                    tool_call["function"]["arguments"]
                )
            except (KeyError, _json.JSONDecodeError):
                args = {}

            result = await execute_tool(func_name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": result
            })

            if func_name == "finish":
                return args.get("summary", "Plan completed.")

    # Extract final text
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            return msg["content"].strip()

    return "No plan generated."
