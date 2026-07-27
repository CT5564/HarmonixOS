# AI Cog.
# Handles all AI-related commands and interactions.

import json

import discord
from discord.ext import commands
from discord import app_commands

from services.ai_service import ask
from services.dispatcher import dispatch
from services.codebase_service import (
    search_and_read,
    search_codebase,
    read_specific_file,
)
from agents.plan import plan_agent
from agents.build import build_agent


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

            answer = await ask(
                prompt,
                author_id=str(interaction.user.id),
                author_name=(
                    interaction.user.nick
                    or interaction.user.global_name
                    or interaction.user.name
                )
            )

            if len(answer) > 1900:
                answer = answer[:1900] + "\n..."

            await interaction.followup.send(answer)

        except Exception as e:

            await interaction.followup.send(
                "❌ Something went wrong."
            )

            print(f"[AI Error] {e}")


    # ============================================================
    # /plan COMMAND
    # ============================================================

    @app_commands.command(
        name="plan",
        description="Plan a task or feature."
    )
    async def plan_task(
        self,
        interaction,
        task: str
    ):

        await interaction.response.defer(
            thinking=True
        )

        try:

            plan = await plan_agent(
                task,
                author_id=str(interaction.user.id),
                author_name=(
                    interaction.user.nick
                    or interaction.user.global_name
                    or interaction.user.name
                )
            )

            if len(plan) > 1900:
                plan = plan[:1900] + "\n..."

            await interaction.followup.send(plan)

        except Exception as e:

            await interaction.followup.send(
                "❌ Failed to create plan."
            )

            print(f"[Plan Error] {e}")


    # ============================================================
    # /build COMMAND
    # ============================================================

    @app_commands.command(
        name="build",
        description="Build or modify code."
    )
    async def build_code(
        self,
        interaction,
        task: str
    ):

        await interaction.response.defer(
            thinking=True
        )

        try:

            result = await build_agent(
                task,
                author_id=str(interaction.user.id),
                author_name=(
                    interaction.user.nick
                    or interaction.user.global_name
                    or interaction.user.name
                )
            )

            summary = result.get(
                "summary", "No summary."
            )
            edits = result.get("edits", [])

            if edits:
                edit_lines = [
                    f"`{e['file']}` — {e['action']}"
                    for e in edits
                ]
                footer = (
                    "\n\n**Files changed:**\n"
                    + "\n".join(edit_lines)
                )
            else:
                footer = ""

            if len(summary) > 1800:
                summary = summary[:1800] + "\n..."

            await interaction.followup.send(
                f"**Build complete**\n\n{summary}{footer}"
            )

        except Exception as e:

            await interaction.followup.send(
                "❌ Build failed."
            )

            print(f"[Build Error] {e}")


    # ============================================================
    # /code COMMAND - Search the codebase
    # ============================================================

    @app_commands.command(
        name="code",
        description="Search Harmonix's source code."
    )
    async def code_search(
        self,
        interaction,
        query: str
    ):

        await interaction.response.defer(thinking=True)

        try:

            results = await search_codebase(query)

            if not results:
                await interaction.followup.send(
                    "No results found."
                )
                return

            if len(results) > 1900:
                results = results[:1900] + "\n..."

            await interaction.followup.send(results)

        except Exception as e:

            await interaction.followup.send(
                "❌ Error searching the codebase."
            )

            print(f"[Code Search Error] {e}")


    # ============================================================
    # /read COMMAND - Read a specific file
    # ============================================================

    @app_commands.command(
        name="read",
        description="Read a file from Harmonix's codebase."
    )
    async def read_file_cmd(
        self,
        interaction,
        filepath: str
    ):

        await interaction.response.defer(thinking=True)

        try:

            content = await read_specific_file(filepath)

            if len(content) > 1900:
                content = content[:1900] + "\n..."

            await interaction.followup.send(content)

        except Exception as e:

            await interaction.followup.send(
                "❌ Error reading that file."
            )

            print(f"[File Read Error] {e}")


    # ============================================================
    # CHAT CHANNEL LISTENER
    # ============================================================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.channel.name != "chat":
            return

        if message.mentions and self.bot.user not in message.mentions:
            return

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

        if not content:
            return

        try:

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

            if len(answer) <= 1900:

                await message.reply(answer)

            else:

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
