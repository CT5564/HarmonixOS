import asyncio

from services.ai_service import ask


async def main():

    response = await ask(
        "Explain recursion in simple terms."
    )

    print("\nHarmonix says:\n")
    print(response)


asyncio.run(main())