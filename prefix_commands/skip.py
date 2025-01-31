import discord
from discord.ext import commands
from libs.music.core import players

def setup(bot):
    """Setup the skip command"""
    @bot.command(name='skip')
    async def skip(ctx):
        """Skip the current song"""
        if not ctx.voice_client or not players[ctx.guild.id].is_playing:
            await ctx.send("Nothing is playing right now!")
            return
            
        ctx.voice_client.stop()  # This will trigger the after callback and play next song
        
        embed = discord.Embed(
            title="⏭️ Skipped",
            description="Playing next song in queue...",
            color=0x89CFF0
        )
        await ctx.send(embed=embed)