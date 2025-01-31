import discord
from discord.ext import commands
from datetime import timedelta
from libs.music.core import players

def setup(bot):
    """Setup the queue command"""
    @bot.command(name='queue')
    async def queue(ctx):
        """Show the current queue"""
        if ctx.guild.id not in players or not players[ctx.guild.id].queue:
            await ctx.send("The queue is empty!")
            return
            
        player = players[ctx.guild.id]
        
        embed = discord.Embed(
            title="🎵 Queue",
            color=0x89CFF0
        )
        
        # Add current song
        if player.current_song:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current_song.name}** ({player.current_song.formatted_duration}) - Requested by {player.current_song.requester.display_name}",
                inline=False
            )
        
        # Add queue
        queue_str = ""
        total_duration = sum(song.duration for song in player.queue)
        
        for i, song in enumerate(player.queue, 1):
            queue_str += f"{i}. **{song.name}** ({song.formatted_duration}) - Requested by {song.requester.display_name}\n"
            if i >= 10:  # Only show first 10 songs
                remaining = len(player.queue) - 10
                if remaining > 0:
                    queue_str += f"...and {remaining} more"
                break
        
        if queue_str:
            embed.add_field(
                name="Up Next",
                value=queue_str,
                inline=False
            )
            
            # Add total duration field
            total_duration_formatted = str(timedelta(seconds=total_duration)).split(".")[0]  # Remove microseconds
            embed.add_field(
                name="Total Queue Duration",
                value=total_duration_formatted,
                inline=True
            )
            
            embed.add_field(
                name="Songs in Queue",
                value=str(len(player.queue)),
                inline=True
            )
            
        await ctx.send(embed=embed)