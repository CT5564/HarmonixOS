from discord.ext import commands
from discord import app_commands

from services.database import add_task, get_tasks


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

        message = "## 📅 Today's Tasks\n\n"

        for task in tasks:
            message += f"• {task[1]}\n"

        await interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(Tasks(bot))