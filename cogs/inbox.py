# Inbox Cog. Handles messages sent to the bot's inbox channel.

from discord.ext import commands
from discord import app_commands

from services.dispatcher import dispatch


class Inbox(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="harmonix",
        description="Talk to Harmonix naturally."
    )
    async def harmonix(
        self,
        interaction,
        message: str
    ):

        await interaction.response.defer()

        response = await dispatch(message)

        await interaction.followup.send(response)
    # Message listener (future primary interface)
    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignore bots
        if message.author.bot:
            return

        # Only listen in the inbox channel
        if message.channel.name != "inbox":
            return

        response = await dispatch(message.content)

        await message.reply(response)


async def setup(bot):
    await bot.add_cog(Inbox(bot))