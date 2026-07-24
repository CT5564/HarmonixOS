# AI Cog.
# Handles all AI-related commands and interactions.

from discord.ext import commands
from discord import app_commands
from services.ai_service import ask
from services.dispatcher import dispatch


class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ============================================================
    # /ask COMMAND
    # ============================================================

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

        try:

            answer = await ask(prompt)

            # Discord messages have a 2000 character limit
            if len(answer) > 1900:
                answer = answer[:1900] + "\n..."

            await interaction.followup.send(answer)

        except Exception as e:

            await interaction.followup.send(
                "❌ Something went wrong while talking to Harmonix."
            )

            print(f"[AI Error] {e}")


    # ============================================================
    # CHAT CHANNEL LISTENER
    # ============================================================

    @commands.Cog.listener()
    async def on_message(self, message):
        
        # Ignore Harmonix and other bots
        if message.author.bot:
            return


        # Only respond in #chat
        if message.channel.name != "chat":
            return


        # Optional:
        # Ignore messages that mention another bot
        if message.mentions and self.bot.user not in message.mentions:
            return


        # Remove bot mention if Harmonix was mentioned
        content = message.content

        if self.bot.user:

            content = content.replace(
                f"<@{self.bot.user.id}>",
                ""
            ).strip()

            content = content.replace(
                f"<@!{self.bot.user.id}>",
                ""
            ).strip()


        # Don't respond to empty messages
        if not content:
            return


        try:

            # Show typing indicator
            async with message.channel.typing():

                answer = await dispatch(
                    content,
                    author_id=str(message.author.id),
                    author_name=(
                        message.author.nick
                        or message.author.global_name
                        or message.author.name
                    )
                )


            # Discord messages have a 2000 character limit
            if len(answer) <= 1900:

                await message.reply(answer)

            else:

                # Split response into chunks
                chunks = [
                    answer[i:i + 1900]
                    for i in range(0, len(answer), 1900)
                ]

                for chunk in chunks:

                    await message.reply(chunk)


        except Exception as e:

            print(f"[AI Chat Error] {e}")

            await message.reply(
                "❌ I couldn't process that message."
            )


async def setup(bot):

    await bot.add_cog(AI(bot))