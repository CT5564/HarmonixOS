# General Cog. Contains general commands for the bot.

from discord.ext import commands
from discord import app_commands


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Check if Harmonix is online."
    )
    async def ping(self, interaction):

        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong!\nLatency: {latency} ms"
        )


async def setup(bot):
    await bot.add_cog(General(bot))