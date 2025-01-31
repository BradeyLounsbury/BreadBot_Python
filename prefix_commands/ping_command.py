from discord.ext import commands

def setup(bot):
    """Setup the ping command"""
    @bot.command(name='ping')
    async def ping(ctx):
        """Check bot's latency"""
        latency = round(bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')