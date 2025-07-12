from discord.ext import commands
from utils.reminder import send_reminder

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remindme(self, ctx, *, message: str):
        """Test gửi nhắc nhở cho chính bạn."""
        event = {"title": message, "reminder_time": "trong 15 phút", "description": ""}
        await send_reminder(self.bot, ctx.author.id, event)
        await ctx.send("Đã gửi nhắc nhở qua DM!")

async def setup(bot):
    await bot.add_cog(Reminder(bot))
