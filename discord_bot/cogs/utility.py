from discord.ext import commands
from discord import __version__ as discord_version

class Utility(commands.Cog):
    """Các lệnh tiện ích."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Kiểm tra ping bot."""
        await ctx.send(f"Pong! Độ trễ: {round(self.bot.latency*1000)} ms")

    @commands.command()
    async def version(self, ctx):
        """Xem version của bot và thư viện discord.py."""
        await ctx.send(f"Bot đang chạy discord.py version {discord_version}")
        
async def setup(bot):
    await bot.add_cog(Utility(bot))