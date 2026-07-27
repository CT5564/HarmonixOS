# Router Cog. Contains commands for testing the router service.

from discord.ext import commands
from discord import app_commands

from services.router import classify

from services.log import get_log
log = get_log(__name__)


class Classify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="classify",
        description="Test the router."
    )
    async def classify_command(
        self,
        interaction,
        message: str
    ):
        log.debug("Route 1")

        await interaction.response.defer()

        log.debug("Route 2")

        intent = await classify(message)

        log.debug("Route 3")

        await interaction.followup.send(
            f"{intent.value}"
        )

        log.debug("Route 4")


async def setup(bot):
    await bot.add_cog(Classify(bot))