import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from services.database import initialize_database
from services.logger import logger
from services import sync_service
from services.webhook_server import start_server
from config import DEV_CHANNEL, NOTION_WEBHOOK_PORT


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")

        for cmd in synced:
            print(f"- {cmd.name} | ID: {cmd.id}")

    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

    logger.setup(bot, DEV_CHANNEL)

    # ========================================================
    # NOTION SYNC — initial pull + webhook server
    # ========================================================

    try:

        await sync_service.initial_sync()

    except Exception as e:

        print(
            f"[Sync] Initial sync failed: {e}"
        )

    try:

        await start_server(NOTION_WEBHOOK_PORT)

    except Exception as e:

        print(
            f"[Webhook] Server failed to start: "
            f"{e}"
        )

    # ========================================================

    await logger.startup(
        f"""
    **Version**
    0.6.0

    **Model**
    auto/best-fast

    **Guilds**
    {len(bot.guilds)}

    **Commands**
    {len(bot.tree.get_commands())}

    **Notion Sync**
    Active (webhook port {NOTION_WEBHOOK_PORT})
    """
    )


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded {filename}")

async def main():
    initialize_database()

    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
