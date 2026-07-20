# This File manages the task commands for the bot.
# Purely frontend, all backend logic is in services/task_service.py

from discord.ext import commands
from discord import app_commands
from services.entity_extractor import extract_task
import services.task_service as task_service

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="capture",
        description="Capture a task."
    )
    async def capture(
        self,
        interaction,
        task: str
    ):
        
        await interaction.response.defer(thinking=True)

        entity = await extract_task(task)

        await task_service.create_task(entity)

        await interaction.followup.send(
            f"✅ Saved:\n**{entity.title}**"
        )

    @app_commands.command(
        name="today",
        description="Show today's tasks."
    )
    async def today(
        self,
        interaction
    ):
        
        await interaction.response.defer(thinking=True)

        tasks = await task_service.get_all_tasks()
        if not tasks:
            return "🎉 No tasks."

        msg = "# 📋 Tasks\n\n"

        for task in tasks:
            msg += f"`#{task[0]}` • {task[1]}\n"

        await interaction.followup.send(msg)

    @app_commands.command(
        name="done",
        description="Mark a task as completed."
    )
    
    async def done(self, interaction, task_id: int):
        await interaction.response.defer(thinking=True)
        # Mark the task completed and notify the user
        await task_service.complete_task_by_id(task_id)

        await interaction.followup.send(
            f"✅ Task #{task_id} completed!"
        )
    
    @app_commands.command(
        name="delete",
        description="Delete a task."
    )
    async def delete(
        self,
        interaction,
        task_id: int
    ):

        await interaction.response.defer(thinking=True)
        await task_service.delete_task_by_id(task_id)

        await interaction.followup.send(
            f"🗑️ Deleted task #{task_id}"
        )

    @app_commands.command(
        name="edit",
        description="Edit a task."
    )
    async def edit(
        self,
        interaction,
        task_id: int,
        new_text: str
    ):

        await interaction.response.defer(thinking=True)
        await task_service.edit_task(
            task_id,
            new_text
        )

        await interaction.followup.send(
            f"✏️ Updated task #{task_id}"
        )

    @app_commands.command(
        name="search",
        description="Search tasks."
    )
    async def search(
        self,
        interaction,
        keyword: str
    ):

        await interaction.response.defer(thinking=True)
        tasks = await task_service.search_for_tasks(keyword)

        if not tasks:
            await interaction.followup.send(
                "Nothing found."
            )
            return

        msg = "# 🔎 Results\n\n"

        for task in tasks:
            msg += f"`#{task[0]}` • {task[1]}\n"

        await interaction.followup.send(msg)

async def setup(bot):
    await bot.add_cog(Tasks(bot))