from discord.ext import commands
import discord

class Moderation(commands.Cog):
    """Các lệnh quản trị server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick thành viên khỏi server."""
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Đã kick {member.mention}")
        except Exception as e:
            await ctx.send(f"Không thể kick: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban thành viên khỏi server."""
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Đã ban {member.mention}")
        except Exception as e:
            await ctx.send(f"Không thể ban: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))