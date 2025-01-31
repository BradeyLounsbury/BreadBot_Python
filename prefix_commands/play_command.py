import discord
from discord.ext import commands
import os

def setup(bot):
    """Setup the play and pause commands"""
    
    @bot.command(name='play')
    async def play(ctx, filename: str):
        """Play an audio file in the user's voice channel
        
        Parameters:
        filename (str): Name of the audio file to play (without extension)
        """
        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return
            
        # Get the voice channel
        voice_channel = ctx.author.voice.channel
        
        # Common audio extensions
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
        
        # Try to find the file with any supported extension
        full_path = None
        actual_filename = None
        
        for ext in audio_extensions:
            test_path = f"audio/{filename}{ext}"
            if os.path.exists(test_path):
                full_path = test_path
                actual_filename = f"{filename}{ext}"
                break
                
        if not full_path:
            await ctx.send(f"Could not find audio file: {filename}\nTry one of these extensions: {', '.join(audio_extensions)}")
            return
            
        try:
            # Connect to voice channel if not already connected
            if ctx.voice_client is None:
                await voice_channel.connect()
            elif ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
                
            # Stop any current audio
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                
            # Play the audio file
            audio_source = discord.FFmpegPCMAudio(full_path)
            ctx.voice_client.play(audio_source)
            await ctx.send(f"Now playing: {filename}")
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            
    @bot.command(name='pause')
    async def pause(ctx):
        """Pause or resume the current audio"""
        if not ctx.voice_client:
            await ctx.send("I'm not currently playing anything!")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused ⏸️")
        elif ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed ▶️")
        else:
            await ctx.send("Nothing is currently playing!")