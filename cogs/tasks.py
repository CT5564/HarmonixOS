from discord.ext import commands
from services.database import add_task

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def capture(self, ctx, *, task):

        add_task(task)

        await ctx.send(f"Saved: {task}")

async def setup(bot):
    await bot.add_cog(Tasks(bot))