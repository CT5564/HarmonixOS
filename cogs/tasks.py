# This File manages the task commands for the bot.
# Purely frontend, all backend logic is in services/task_service.py
import discord

from discord.ext import commands, tasks
from discord import app_commands

from datetime import time
from zoneinfo import ZoneInfo

from services.entity_extractor import extract_task
from services.dispatcher import dispatch
from services import task_service

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        # Philippines timezone
        self.ph_timezone = ZoneInfo("Asia/Manila")

        # Start daily #today scheduler
        self.daily_today.start()

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
    async def today(self, interaction):

        today_tasks = await task_service.get_today_tasks()
        overdue_tasks = await task_service.get_overdue_tasks()

        if not today_tasks and not overdue_tasks:

            await interaction.response.send_message(
                "🎉 You're all caught up!"
            )

            return

        message = "📅 **Today's Tasks**\n\n"

        # --------------------------------------------------------
        # OVERDUE
        # --------------------------------------------------------

        if overdue_tasks:

            message += "🔴 **OVERDUE**\n\n"

            for task in overdue_tasks:

                message += (
                    f"`#{task[0]}` • **{task[1]}**\n"
                    f"   📅 Due: {task[4]}\n"
                )

                if task[3]:
                    message += f"   ⚡ Priority: {task[3]}\n"

                message += "\n"

        # --------------------------------------------------------
        # TODAY
        # --------------------------------------------------------

        if today_tasks:

            message += "🟡 **DUE TODAY**\n\n"

            for task in today_tasks:

                message += (
                    f"`#{task[0]}` • **{task[1]}**\n"
                )

                if task[5]:
                    message += f"   ⏰ {task[5]}\n"

                if task[3]:
                    message += f"   ⚡ Priority: {task[3]}\n"

                if task[6]:
                    message += f"   📂 {task[6]}\n"

                message += "\n"

        await interaction.response.send_message(message)

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







    def cog_unload(self):

        self.daily_today.cancel()


    # ============================================================
    # TODAY MESSAGE FORMATTER
    # ============================================================

    async def build_today_message(self):

        # Get tasks
        today_tasks = await task_service.get_today_tasks()

        overdue_tasks = await task_service.get_overdue_tasks()


        # Start message
        message = "## 📅 Today's Tasks\n\n"


        # ========================================================
        # OVERDUE TASKS
        # ========================================================

        if overdue_tasks:

            message += "### 🔴 Overdue\n\n"

            for task in overdue_tasks:

                message += (
                    f"**`#{task[0]}` {task[1]}**\n"
                )

                if task[4]:

                    message += (
                        f"📅 Due: {task[4]}\n"
                    )

                if task[3]:

                    message += (
                        f"⚡ Priority: {task[3]}\n"
                    )

                if task[6]:

                    message += (
                        f"📂 Project: {task[6]}\n"
                    )

                message += "\n"


        # ========================================================
        # TODAY'S TASKS
        # ========================================================

        if today_tasks:

            message += "### 🟡 Due Today\n\n"

            for task in today_tasks:

                message += (
                    f"**`#{task[0]}` {task[1]}**\n"
                )

                if task[5]:

                    message += (
                        f"⏰ {task[5]}\n"
                    )

                if task[3]:

                    message += (
                        f"⚡ Priority: {task[3]}\n"
                    )

                if task[6]:

                    message += (
                        f"📂 Project: {task[6]}\n"
                    )

                message += "\n"


        # ========================================================
        # NO TASKS
        # ========================================================

        if not today_tasks and not overdue_tasks:

            message += (
                "🎉 **You're all caught up!**\n"
                "Nothing scheduled for today."
            )


        return message


    # ============================================================
    # /TODAY COMMAND
    # ============================================================

    @app_commands.command(
        name="today",
        description="Show today's tasks."
    )
    async def today(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer()

        try:

            message = await self.build_today_message()

            await interaction.followup.send(
                message
            )

        except Exception as e:

            print(
                f"[Today Command Error] {e}"
            )

            await interaction.followup.send(
                "❌ I couldn't load today's tasks."
            )


    # ============================================================
    # DAILY #TODAY SCHEDULER
    # ============================================================

    @tasks.loop(
        time=time(
            hour=7,
            minute=0,
            tzinfo=ZoneInfo("Asia/Manila")
        )
    )
    async def daily_today(self):

        # Find #today channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            name="today"
        )

        if channel is None:

            print(
                "❌ Could not find #today channel."
            )

            return


        try:

            message = await self.build_today_message()

            await channel.send(
                message
            )

            print(
                "📅 Daily #today message sent."
            )

        except Exception as e:

            print(
                f"[Daily Today Error] {e}"
            )


    # ============================================================
    # SCHEDULER READY CHECK
    # ============================================================

    @daily_today.before_loop
    async def before_daily_today(self):

        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Tasks(bot))