from discord.ext import commands

class Moderation(commands.Cog):
    """Các lệnh quản trị server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member, *, reason=None):
        """Kick thành viên khỏi server."""
        await member.kick(reason=reason)
        await ctx.send(f"Đã kick {member.mention}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member, *, reason=None):
        """Ban thành viên khỏi server."""
        await member.ban(reason=reason)
        await ctx.send(f"Đã ban {member.mention}")

def setup(bot):
    bot.add_cog(Moderation(bot))