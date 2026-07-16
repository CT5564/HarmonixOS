import discord
from datetime import datetime


class Logger:

    def __init__(self):
        self.bot = None
        self.channel_id = None

    def setup(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    async def _send(self, level, emoji, message):

        if self.bot is None:
            return

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        await channel.send(
            f"{emoji} **{level}** • `{timestamp}`\n{message}"
        )

    async def info(self, message):
        await self._send("INFO", "🟢", message)

    async def warning(self, message):
        await self._send("WARNING", "🟡", message)

    async def error(self, message):
        await self._send("ERROR", "🔴", message)

    async def ai(self, message):
        await self._send("AI", "🔵", message)

    async def task(self, message):
        await self._send("TASK", "🟣", message)

    async def startup(self, message):
        await self._send("STARTUP", "🚀", message)


logger = Logger()