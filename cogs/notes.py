# Notes Cog. Contains commands for managing notes.

from discord.ext import commands
from discord import app_commands

import services.note_service as note_service

from services.log import get_log
log = get_log(__name__)


class Notes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="note",
        description="Save a note."
    )
    async def note(
        self,
        interaction,
        content: str
    ):

        await note_service.create_note(
            content,
            author_id=str(interaction.user.id),
            author_name=(
                interaction.user.nick
                or interaction.user.global_name
                or interaction.user.name
            )
        )

        await interaction.response.send_message(
            f"📝 Saved:\n**{content}**"
        )

    @app_commands.command(
        name="notes",
        description="Show all notes."
    )
    async def notes(
        self,
        interaction
    ):
        log.debug("Notes command called")
        notes = await note_service.get_notes()

        if not notes:
            await interaction.response.send_message(
                "📝 No notes."
            )
            return

        message = "# 📝 Notes\n\n"

        for note in notes:
            message += f"`#{note[0]}` • {note[1]}\n"

        await interaction.response.send_message(message)

    @app_commands.command(
        name="delete_note",
        description="Delete a note."
    )
    async def delete_note(
        self,
        interaction,
        note_id: int
    ):

        await note_service.delete_note_by_id(note_id)

        await interaction.response.send_message(
            f"🗑️ Deleted note #{note_id}"
        )

    @app_commands.command(
        name="edit_note",
        description="Edit a note."
    )
    async def edit_note(
        self,
        interaction,
        note_id: int,
        new_text: str
    ):

        await note_service.edit_note(
            note_id,
            new_text
        )

        await interaction.response.send_message(
            f"✏️ Updated note #{note_id}"
        )

    @app_commands.command(
        name="search_notes",
        description="Search notes."
    )
    async def search_notes(
        self,
        interaction,
        keyword: str
    ):

        notes = await note_service.search_for_notes(keyword)

        if not notes:
            await interaction.response.send_message(
                "Nothing found."
            )
            return

        msg = "# 🔎 Notes\n\n"

        for note in notes:
            msg += f"`#{note[0]}` • {note[1]}\n"

        await interaction.response.send_message(msg)


async def setup(bot):
    await bot.add_cog(Notes(bot))