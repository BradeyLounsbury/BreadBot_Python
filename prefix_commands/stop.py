import discord
from discord.ext import commands
from libs.music.core import players

def setup(bot):
    """Setup the stop command"""
    @bot.command(name='stop')
    async def stop(ctx):
        """Stop playing music, clear the queue, and disconnect from voice channel"""
        if not ctx.voice_client:
            await ctx.send("I'm not connected to a voice channel!")
            return
            
        # Check if there's an active player for this guild
        if ctx.guild.id not in players:
            await ctx.send("No active music player found!")
            return
            
        player = players[ctx.guild.id]
        
        # Cancel any current update task if it exists
        if player.current_update_task and not player.current_update_task.done():
            player.current_update_task.cancel()
        
        # Clear the queue and reset player state
        player.clear_queue()
        player.is_playing = False
        player.is_paused = False
        
        # Stop audio and disconnect
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
        
        await ctx.voice_client.disconnect()
        
        # Send confirmation embed
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Music playback stopped and queue cleared.",
            color=0x89CFF0
        )
        await ctx.send(embed=embed)