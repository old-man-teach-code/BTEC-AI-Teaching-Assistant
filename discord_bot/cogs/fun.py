
from discord.ext import commands
import random

class Fun(commands.Cog):
    """Lệnh vui nhộn."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, dice: str = "1d6"):
        """Quay xúc xắc. Ví dụ: !roll 2d10"""
        try:
            rolls, limit = map(int, dice.lower().split("d"))
        except Exception:
            await ctx.send("Cú pháp: !roll 2d6")
            return
        result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
        await ctx.send(f"Kết quả: {result}")

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Xin chào, {ctx.author.mention}!")

async def setup(bot):
    await bot.add_cog(Fun(bot))
