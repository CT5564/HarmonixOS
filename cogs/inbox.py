# Inbox Cog.
# Handles messages sent to the bot's inbox channel.

from discord.ext import commands
from discord import app_commands

from services.dispatcher import dispatch


class Inbox(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ============================================================
    # /HARMONIX COMMAND
    # ============================================================

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

        response = await dispatch(
            message,
            author_id=str(
                interaction.user.id
            ),
            author_name=(
                interaction.user.nick
                or interaction.user.global_name
                or interaction.user.name
            )
        )

        await interaction.followup.send(
            response
        )


    # ============================================================
    # INBOX MESSAGE LISTENER
    # ============================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        # Ignore bots
        if message.author.bot:
            return


        # Only listen in the inbox channel
        if message.channel.name != "inbox":
            return


        response = await dispatch(
            message.content,
            author_id=str(
                message.author.id
            ),
            author_name=(
                message.author.nick
                or message.author.global_name
                or message.author.name
            )
        )


        await message.reply(
            response
        )


async def setup(bot):

    await bot.add_cog(
        Inbox(bot)
    )