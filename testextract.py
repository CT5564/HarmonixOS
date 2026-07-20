import asyncio

from services.entity_extractor import extract_task


async def main():

    task = await extract_task(
        "Finish CMSC 123 Machine Problem tomorrow at 5 PM."
    )

    print(task)


asyncio.run(main())