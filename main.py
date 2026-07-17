import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from services.database import initialize_database


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DEV_CHANNEL = int(os.getenv("DEV_CHANNEL"))

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
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")


    #Logger setup
    logger.setup(bot, DEV_CHANNEL)

    await logger.startup(
        f"""
    **Version**
    0.1.0

    **Model**
    llama3.2:3b

    **Guilds**
    {len(bot.guilds)}

    **Commands**
    {len(bot.tree.get_commands())}
    """
    )

import os

#logger setup
from services.logger import logger
from config import DEV_CHANNEL

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