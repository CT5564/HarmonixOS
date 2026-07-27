# This File manages the task commands for the bot.
# Purely frontend, all backend logic is in services/task_service.py
import discord

from discord.ext import commands, tasks
from discord import app_commands

from datetime import date, time
from zoneinfo import ZoneInfo

from services.entity_extractor import extract_task
from services.dispatcher import dispatch
from services.project_service import get_project_names
from services import task_service
from services import sync_service
from services import database as db

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Philippines timezone
        self.ph_timezone = ZoneInfo("Asia/Manila")

        # Start daily #today scheduler
        self.daily_today.start()

    # ============================================================
    # COG LOAD — auto-send today message on startup
    # ============================================================

    async def cog_load(self):
        self.bot.loop.create_task(
            self.send_startup_today()
        )

    async def send_startup_today(self):
        await self.bot.wait_until_ready()

        import asyncio
        await asyncio.sleep(3)

        channel = discord.utils.get(
            self.bot.get_all_channels(),
            name="today"
        )

        if channel is None:
            print(
                "[Startup] #today channel not found."
            )
            return

        today_str = date.today().isoformat()

        async for message in channel.history(
            limit=20
        ):
            if (
                message.author == self.bot.user
                and message.created_at.date().isoformat()
                == today_str
            ):
                print(
                    "[Startup] Today message already "
                    "sent. Skipping."
                )
                return

        try:
            content = await self.build_today_message(
                None
            )
            await channel.send(content)
            print(
                "[Startup] Sent today message."
            )
        except Exception as e:
            print(
                f"[Startup Today Error] {e}"
            )

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

        author_id = str(interaction.user.id)
        projects = await get_project_names()

        entity = await extract_task(
            task,
            author_id,
            projects
        )

        await task_service.create_task(entity)

        await interaction.followup.send(
            f"✅ Saved:\n**{entity.title}**"
        )

        # Push to Notion in background
        import asyncio
        asyncio.create_task(
            sync_service.push_to_notion({
                "title": entity.title,
                "description": entity.description,
                "status": "todo",
                "priority": entity.priority,
                "due_date": entity.due_date,
                "due_time": entity.due_time,
                "project": entity.project,
                "tags": entity.tags,
                "type": (
                    entity.tags[0]
                    if entity.tags
                    else None
                ),
            })
        )



    @app_commands.command(
        name="done",
        description="Mark a task as completed."
    )

    async def done(self, interaction, task_id: int):
        await interaction.response.defer(thinking=True)
        author_id = str(interaction.user.id)

        row = db.get_task_by_id(task_id)

        await task_service.complete_task_by_id(
            task_id,
            author_id
        )

        await interaction.followup.send(
            f"✅ Task #{task_id} completed!"
        )

        # Push completion to Notion
        if row and row[11]:
            import asyncio
            asyncio.create_task(
                sync_service.push_to_notion({
                    "id": row[0],
                    "title": row[2],
                    "status": "completed",
                    "priority": row[5],
                    "due_date": row[6],
                    "due_time": row[7],
                    "project": row[8],
                    "tags": (
                        __import__("json").loads(
                            row[9]
                        ) if row[9] else []
                    ),
                    "type": row[10],
                    "notion_page_id": row[11],
                })
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
        author_id = str(interaction.user.id)

        row = db.get_task_by_id(task_id)

        await task_service.delete_task_by_id(
            task_id,
            author_id
        )

        await interaction.followup.send(
            f"🗑️ Deleted task #{task_id}"
        )

        # Trash in Notion
        if row and row[11]:
            import asyncio
            asyncio.create_task(
                sync_service.delete_in_notion({
                    "notion_page_id": row[11],
                })
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
        author_id = str(interaction.user.id)

        row = db.get_task_by_id(task_id)

        await task_service.edit_task(
            task_id,
            author_id,
            new_text
        )

        await interaction.followup.send(
            f"✏️ Updated task #{task_id}"
        )

        # Push update to Notion
        if row and row[11]:
            import asyncio
            asyncio.create_task(
                sync_service.push_to_notion({
                    "id": row[0],
                    "title": new_text,
                    "status": row[4],
                    "priority": row[5],
                    "due_date": row[6],
                    "due_time": row[7],
                    "project": row[8],
                    "tags": (
                        __import__("json").loads(
                            row[9]
                        ) if row[9] else []
                    ),
                    "type": row[10],
                    "notion_page_id": row[11],
                })
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
        author_id = str(interaction.user.id)

        # Search all tasks for owner
        if author_id == "753163813020499968":
            author_id = None

        tasks = await task_service.search_for_tasks(
            author_id,
            keyword
        )

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

    PRIORITY_EMOJI = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    def _format_task(self, task, show_date=False):
        task_id, title, desc, priority, due_date, \
            due_time, project, tags, *rest = task

        emoji = self.PRIORITY_EMOJI.get(
            priority, ""
        )

        line = f"`#{task_id}` {emoji} **{title}**"

        details = []

        if show_date and due_date:
            details.append(f"📅 {due_date}")

        if due_time:
            details.append(f"⏰ {due_time}")

        if project:
            details.append(f"📂 {project}")

        if details:
            line += "\n" + " · ".join(details)

        return line


    async def build_today_message(
        self,
        author_id: str | None = None
    ):

        today = date.today()
        today_str = today.isoformat()

        overdue_tasks = await task_service.get_overdue_tasks(
            author_id
        )

        today_tasks = await task_service.get_today_tasks(
            author_id
        )

        upcoming_tasks = await task_service.get_upcoming_tasks(
            author_id
        )

        total = (
            len(overdue_tasks)
            + len(today_tasks)
            + len(upcoming_tasks)
        )

        message = "## 📅 Today\n\n"

        # ========================================================
        # SUMMARY LINE
        # ========================================================

        parts = []

        if overdue_tasks:
            parts.append(
                f"**{len(overdue_tasks)}** overdue"
            )

        if today_tasks:
            parts.append(
                f"**{len(today_tasks)}** due today"
            )

        if upcoming_tasks:
            parts.append(
                f"**{len(upcoming_tasks)}** upcoming"
            )

        if parts:
            message += " · ".join(parts) + "\n\n"

        # ========================================================
        # OVERDUE TASKS
        # ========================================================

        if overdue_tasks:

            message += "### 🔴 Overdue\n\n"

            for task in overdue_tasks:
                message += (
                    self._format_task(task)
                    + "\n"
                )

            message += "\n"

        # ========================================================
        # TODAY'S TASKS
        # ========================================================

        if today_tasks:

            message += "### 🟡 Today\n\n"

            for task in today_tasks:
                message += (
                    self._format_task(task)
                    + "\n"
                )

            message += "\n"

        # ========================================================
        # UPCOMING TASKS — grouped by date
        # ========================================================

        if upcoming_tasks:

            by_date: dict[str, list] = {}

            for task in upcoming_tasks:
                d = task[4]
                by_date.setdefault(d, []).append(
                    task
                )

            message += "### 🔵 Upcoming\n\n"

            for d, tasks in by_date.items():
                dt = date.fromisoformat(d)
                diff = (dt - today).days
                day_name = dt.strftime("%a")

                if diff == 1:
                    label = "Tomorrow"
                else:
                    label = f"{day_name} ({diff}d)"

                message += (
                    f"**{label} — {d}**\n"
                )

                for task in tasks:
                    message += (
                        self._format_task(task)
                        + "\n"
                    )

                message += "\n"

        # ========================================================
        # NO TASKS
        # ========================================================

        if total == 0:

            message += (
                "🎉 **You're all caught up!**\n"
                "Nothing scheduled."
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

            author_id = str(
                interaction.user.id
            )

            # Show all tasks for owner
            if author_id == "753163813020499968":
                author_id = None

            message = await self.build_today_message(
                author_id
            )

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

            message = await self.build_today_message(None)

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
