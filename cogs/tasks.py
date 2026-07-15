from discord.ext import commands
from discord import app_commands

from services.database import (
    add_task,
    get_tasks,
    complete_task,
    delete_task,
    update_task,
    search_tasks,
)

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

        add_task(task)

        await interaction.response.send_message(
            f"✅ Saved:\n**{task}**"
        )

    @app_commands.command(
        name="today",
        description="Show today's tasks."
    )
    async def today(
        self,
        interaction
    ):

        tasks = get_tasks()

        if not tasks:
            await interaction.response.send_message(
                "🎉 No tasks!"
            )
            return

        message = "# 📅 Today's Tasks\n\n"

        for task in tasks:
            message += f"`#{task[0]}` • {task[1]}\n"

        await interaction.response.send_message(message)

    @app_commands.command(
        name="done",
        description="Mark a task as completed."
    )
    async def done(
        self,
        interaction,
        task_id: int
    ):
        async def done(self, interaction, task_id: int):
            print("DONE COMMAND CALLED")

            await interaction.response.send_message("Testing!")

        complete_task(task_id)

        await interaction.response.send_message(
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

        delete_task(task_id)

        await interaction.response.send_message(
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

        update_task(task_id, new_text)

        await interaction.response.send_message(
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

        tasks = search_tasks(keyword)

        if not tasks:
            await interaction.response.send_message(
                "Nothing found."
            )
            return

        msg = "# 🔎 Results\n\n"

        for task in tasks:
            msg += f"`#{task[0]}` • {task[1]}\n"

        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(Tasks(bot))