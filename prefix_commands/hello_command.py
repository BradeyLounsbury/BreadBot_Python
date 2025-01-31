from discord.ext import commands

def setup(bot):
    """Setup the hello command"""
    @bot.command(name='hello')
    async def hello(ctx):
        """Simple command that responds with a greeting"""
        await ctx.send(f'Hello! I am {bot.user.name}! 🍞')