import discord
from discord.ext import commands

def setup(bot):
    """Setup the pause command"""
    @bot.command(name='pause')
    async def pause(ctx):
        """Pause or resume the current audio"""
        if not ctx.voice_client:
            await ctx.send("I'm not currently playing anything!")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            
            # Create pause embed
            embed = discord.Embed(
                title="⏸️ Paused",
                description="Use `-pause` again to resume",
                color=0x89CFF0
            )
            await ctx.send(embed=embed)
            
        elif ctx.voice_client.is_paused():
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