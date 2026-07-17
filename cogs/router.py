# Router Cog. Contains commands for testing the router service.

from discord.ext import commands
from discord import app_commands

from services.router import classify


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
        print("1")

        await interaction.response.defer()

        print("2")

        intent = await classify(message)

        print("3")

        await interaction.followup.send(
            f"{intent.value}"
        )

        print("4")


async def setup(bot):
    await bot.add_cog(Classify(bot))