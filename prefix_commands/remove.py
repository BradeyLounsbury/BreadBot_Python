import discord
from discord.ext import commands
from libs.music.core import players

def setup(bot):
    """Setup the remove command"""
    @bot.command(name='remove')
    async def remove(ctx, position: int = None):
        """Remove a song from the queue by its position"""
        if ctx.guild.id not in players or not players[ctx.guild.id].queue:
            await ctx.send("The queue is empty!")
            return
            
        player = players[ctx.guild.id]
        queue_length = len(player.queue)
        
        # If no position is provided, show error message
        if position is None:
            await ctx.send("Please specify a position in the queue to remove. Use `-queue` to see all positions.")
            return
        
        # Check if position is valid
        if position < 1 or position > queue_length:
            await ctx.send(f"Invalid position! Please specify a number between 1 and {queue_length}.")
            return
        
        # Get the song to be removed (convert position to 0-based index)
        song = player.queue[position - 1]
        
        # Create embed before removing the song
        embed = discord.Embed(
            title="🗑️ Removed from Queue",
            description=f"**{song.name}** ({song.formatted_duration}) - Requested by {song.requester.display_name}",
            color=0x89CFF0
        )
        
        # Remove the song
        player.queue.remove(song)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='rl')
    async def remove_last(ctx):
        """Remove the last song in the queue"""
        if ctx.guild.id not in players or not players[ctx.guild.id].queue:
            await ctx.send("The queue is empty!")
            return
            
        player = players[ctx.guild.id]
        queue_length = len(player.queue)
        
        # Get the last song
        song = player.queue[queue_length - 1]
        
        # Create embed before removing the song
        embed = discord.Embed(
            title="🗑️ Removed Last Song",
            description=f"**{song.name}** ({song.formatted_duration}) - Requested by {song.requester.display_name}",
            color=0x89CFF0
        )
        
        # Remove the last song
        player.queue.pop()
        
        await ctx.send(embed=embed)