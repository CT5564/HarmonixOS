import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MTUyNjk1MDAxMDk4ODUzMTk1Nw.Gq6fRd.0kMbdp3lTtG-JGVAvhfqLw1BOS8_WVlqnzh1Fk")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

async def load_extensions():
    await bot.load_extension("cogs.general")
    await bot.load_extension("cogs.tasks")
    await bot.load_extension("cogs.ai")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())