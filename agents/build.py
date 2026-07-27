# Build Agent
#
# Uses tool-calling to explore the codebase, read files,
# and make edits. The agent decides what to read and
# what to change — no giant context dumps.

from services.omniroute_client import chat
from agents.tools import TOOL_DEFINITIONS, execute_tool

MODEL = "auto/best-reasoning"

MAX_TOOL_ROUNDS = 20

SYSTEM_PROMPT = """
You are Harmonix's build agent — a careful, precise code editor.

You have tools to search, read, edit, and create files.
Use them to understand the code, then make targeted changes.

Workflow:
1. search_code to find relevant files.
2. read_file to study the code you need to change.
3. edit_file to make precise edits (exact find/replace).
4. create_file for new files.
5. finish when done with a summary.

Rules:
- Preserve existing code style (indentation, naming, patterns).
- Make minimal, targeted changes — don't rewrite entire files.
- Never remove functionality unless explicitly asked.
- Every edit must use an exact character-for-character find string.
- Always read a file before editing it.
- Security: never access files outside the project.
"""


async def build_agent(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> dict:
    """
    Process a build request using tool-calling loop.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    edits_made = []

    for round_num in range(MAX_TOOL_ROUNDS):

        response = await chat(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS
        )

        assistant_msg = response["message"]
        finish = response.get("finish_reason", "stop")

        messages.append(assistant_msg)

        # No tool calls — agent is done
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

            # Track edits
            if func_name == "edit_file" and not result.startswith("ERROR"):
                edits_made.append({
                    "file": args.get("filepath", ""),
                    "action": "edit"
                })
            elif func_name == "create_file" and not result.startswith("ERROR"):
                edits_made.append({
                    "file": args.get("filepath", ""),
                    "action": "create"
                })

            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": result
            })

            if func_name == "finish":
                return {
                    "summary": args.get("summary", "Done"),
                    "edits": edits_made
                }

    # Extract final text response
    final_text = ""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            final_text = msg["content"]
            break

    return {
        "summary": final_text or "Build agent completed.",
        "edits": edits_made
    }
