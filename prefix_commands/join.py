import discord

def setup(bot):
    @bot.command()
    async def join(ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Disconnect from existing voice client if already connected
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
        
        try:
            voice_client = await channel.connect(timeout=60.0, reconnect=True)
            await ctx.send(f"Connected to {channel.name}")
        except discord.errors.ConnectionClosed as e:
            await ctx.send(f"Failed to connect: {e}")
        except Exception as e:
            await ctx.send(f"Error: {e}")