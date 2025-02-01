import discord
from discord.ext import commands
from libs.music.core import MusicPlayer, players

def setup(bot):
    """Setup the pause command"""
    @bot.command(name='pause')
    async def pause(ctx):
        """Pause or resume the current audio"""
        if not ctx.voice_client:
            await ctx.send("I'm not currently playing anything!")
            return
        
        player = players[ctx.guild.id]
        if ctx.voice_client.is_playing():
            player.pause_playback()
            ctx.voice_client.pause()
            
            # Create pause embed
            embed = discord.Embed(
                title="⏸️ Paused",
                description="Use `-pause` again to resume",
                color=0x89CFF0
            )
            await ctx.send(embed=embed)
            
        elif ctx.voice_client.is_paused():
            player.resume_playback()
            ctx.voice_client.resume()
            
            # Create resume embed
            embed = discord.Embed(
                title="▶️ Resumed",
                description="Currently playing music",
                color=0x89CFF0
            )
            await ctx.send(embed=embed)
            
        else:
            await ctx.send("Nothing is currently playing!")