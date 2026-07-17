from discord.ext import commands
from discord import app_commands

from services.ai_service import ask


class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ask",
        description="Ask Harmonix anything."
    )
    async def ask_ai(
        self,
        interaction,
        prompt: str
    ):

        await interaction.response.defer()

        answer = await ask(prompt)
        
        # Discord messages have a 2000 character limit
        if len(answer) > 1900:
            answer = answer[:1900] + "\n..."

        await interaction.followup.send(answer)


async def setup(bot):
    await bot.add_cog(AI(bot))