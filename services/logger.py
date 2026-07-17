import discord
from datetime import datetime


class Logger:

    def __init__(self):
        self.bot = None
        self.channel_id = None

    def setup(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    async def _send(self, title, message, color):

        if self.bot is None:
            return

        channel = await self.bot.fetch_channel(self.channel_id)

        embed = discord.Embed(
            title=title,
            description=message,
            color=color,
            timestamp=datetime.now()
        )

        embed.set_footer(text="Harmonix Logger")

        await channel.send(embed=embed)

    async def startup(self, message):
        await self._send(
            "🚀 STARTUP",
            message,
            discord.Color.green()
        )

    async def info(self, message):
        await self._send(
            "🟢 SYSTEM",
            message,
            discord.Color.blue()
        )

    async def ai(self, message):
        await self._send(
            "🔵 AI",
            message,
            discord.Color.blurple()
        )

    async def task(self, message):
        await self._send(
            "🟣 TASK",
            message,
            discord.Color.purple()
        )

    async def note(self, message):
        await self._send(
            "📝 NOTE",
            message,
            discord.Color.orange()
        )

    async def warning(self, message):
        await self._send(
            "🟡 WARNING",
            message,
            discord.Color.gold()
        )

    async def error(self, message):
        await self._send(
            "🔴 ERROR",
            message,
            discord.Color.red()
        )


logger = Logger()