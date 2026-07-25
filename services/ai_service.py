# AI Service. Handles all interactions with the AI model.

from services.ollama_client import chat
from services.context import build_context
from services.logger import logger

MODEL = "auto/best-fast"

SYSTEM_PROMPT = """
You are Harmonix.

You will receive a MEMORY section.

Primarily use information from MEMORY when answering.

If MEMORY does not contain the answer, search for the answer in your training data or the web.

Do not invent tasks, notes, or projects.
"""
async def ask(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
):

    #Phase 1: Context
    print("[AI] Phase 1: Building user context...")

    current_user_context = ""
    
    if author_name:

        current_user_context = (
            f"\n\nCURRENT USER:\n"
            f"The person currently speaking to you is "
            f"{author_name}."
        )

    try:

        context = await build_context(
            prompt,
            author_id=author_id,
            author_name=author_name
        )

        # Make sure context is valid
        if context is None:

            raise ValueError(
                "build_context() returned None"
            )

        if not isinstance(context, str):

            raise TypeError(
                "build_context() must return a string, "
                f"got {type(context).__name__}"
            )

    except Exception as e:

        print(
            f"[AI Context Error] "
            f"{type(e).__name__}: {e}"
        )

        await logger.error(
                f"""
        ❌ **AI Context Error**

        **User**
        {author_name or "Unknown"}

        **Phase**
        Memory / Context Building

        **Error**
        ```text
        {type(e).__name__}: {e}

        Status
        🔴 Failed
        """
        ) 
        raise

    #Phase 2: Limit context
    print("[AI] Phase 2: Checking context size...")

    MAX_CONTEXT_CHARS = 12000

    original_context_length = len(context)

    if original_context_length > MAX_CONTEXT_CHARS:

        print(
            f"[AI] Context too large: "
            f"{original_context_length:,} characters"
        )

        context = context[:MAX_CONTEXT_CHARS]

        print(
            f"[AI] Context truncated to "
            f"{len(context):,} characters"
        )

    else:

        print(
            f"[AI] Context size OK: "
            f"{len(context):,} characters"
        )

    
    print("Context Built.")


    #Phase 3: System Prompt
    print("[AI] Phase 3: Preparing AI request...")

    system_message = (
        SYSTEM_PROMPT
        + current_user_context
        + "\n\n"
        + "MEMORY:\n"
        + context
    )


    # ============================================================
    # PHASE 4: SEND TO AI
    # ============================================================

    print("[AI] Phase 4: Sending request to AI...")

    try:

        await logger.ai(
            f"""

    🚀 Harmonix AI Request

    User
    {author_name or "Unknown"}

    Model
    {MODEL}

    Prompt Length
    {len(prompt):,} characters

    Memory Context
    {len(context):,} characters

    Phase
    AI Model Request

    Status
    ⏳ Processing
    """
    )

        response = await chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


    except Exception as e:

        print(
            f"[AI Model Error] "
            f"{type(e).__name__}: {e}"
        )

        await logger.error(
            f"""

    ❌ AI Model Error

    User
    {author_name or "Unknown"}

    Model
    {MODEL}

    Phase
    AI Model Request

    Error

    {type(e).__name__}: {e}

    Status
    🔴 Failed
    """
    )

        raise

    # ============================================================
    # PHASE 5: VALIDATE AI RESPONSE
    # ============================================================

    print("[AI] Phase 5: Validating AI response...")

    try:

        if response is None:

            raise ValueError(
                "AI returned None"
            )


        if "message" not in response:

            raise ValueError(
                "AI response does not contain 'message'"
            )


        if response["message"] is None:

            raise ValueError(
                "AI response 'message' is None"
            )


        answer = response["message"].get(
            "content"
        )


        if answer is None:

            raise ValueError(
                "AI response 'content' is None"
            )


        if not isinstance(answer, str):

            raise TypeError(
                "AI response 'content' must be a string, "
                f"got {type(answer).__name__}"
            )


        answer = answer.strip()


    except Exception as e:

        print(
            f"[AI Response Error] "
            f"{type(e).__name__}: {e}"
        )

        await logger.error(
            f"""

    ❌ AI Response Error

    User
    {author_name or "Unknown"}

    Model
    {response.get("model", MODEL) if response else MODEL}

    Phase
    Response Validation

    Error

    {type(e).__name__}: {e}

    Status
    🔴 Failed
    """
    )

        raise


    # ============================================================
    # PHASE 6: LOG COMPLETION
    # ============================================================

    print(
        f"[AI] Phase 6: Request completed. "
        f"Response length: {len(answer):,} characters"
    )


    await logger.ai(
        f"""

    🤖 Harmonix AI Request Completed

    User
    {author_name or "Unknown"}

    Model
    {response.get("model", MODEL)}

    Prompt Length
    {len(prompt):,} characters

    Memory Context
    {len(context):,} characters

    Response Length
    {len(answer):,} characters

    Phase
    AI Response

    Status
    ✅ Completed
    """
    )

    return answer