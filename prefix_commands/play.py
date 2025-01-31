import discord
from discord.ext import commands
import os
import asyncio
from libs.music.core import MusicPlayer, Song, players

async def play_next(ctx, bot):
    """Play the next song in the queue"""
    player = players[ctx.guild.id]
    
    if not player.queue:
        player.is_playing = False
        player.current_song = None
        return

    # Get next song and play it
    next_song = player.get_next_song()
    player.current_song = next_song
    player.is_playing = True

    audio_source = discord.FFmpegPCMAudio(next_song.full_path)
    
    # Create "Now Playing" embed
    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**{next_song.name}**",
        color=0x89CFF0
    )
    embed.add_field(
        name="Requested by",
        value=next_song.requester.display_name,
        inline=True
    )
    embed.add_field(
        name="Duration",
        value=next_song.formatted_duration,
        inline=True
    )
    if next_song.requester.avatar:
        embed.set_thumbnail(url=next_song.requester.avatar.url)
    
    await ctx.send(embed=embed)
    
    ctx.voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
        play_next(ctx, bot), bot.loop).result() if e is None else print(f'Player error: {e}'))

def setup(bot):
    """Setup the play command"""
    @bot.command(name='play')
    async def play(ctx, filename: str):
        """Play an audio file in the user's voice channel or add it to queue"""
        # Initialize player for this guild if it doesn't exist
        if ctx.guild.id not in players:
            players[ctx.guild.id] = MusicPlayer()
        
        player = players[ctx.guild.id]

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
            
            # Create song object with duration detection
            song = Song(actual_filename, full_path, ctx.author)
            
            # If nothing is playing, play this song
            if not player.is_playing:
                player.current_song = song
                player.is_playing = True
                audio_source = discord.FFmpegPCMAudio(full_path)
                
                # Create "Now Playing" embed
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song.name}**",
                    color=0x89CFF0
                )
                embed.add_field(
                    name="Requested by",
                    value=song.requester.display_name,
                    inline=True
                )
                embed.add_field(
                    name="Duration",
                    value=song.formatted_duration,
                    inline=True
                )
                if song.requester.avatar:
                    embed.set_thumbnail(url=song.requester.avatar.url)
                
                await ctx.send(embed=embed)
                
                ctx.voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(ctx, bot), bot.loop).result() if e is None else print(f'Player error: {e}'))
            else:
                # Add to queue
                player.add_to_queue(song)
                
                # Create "Added to Queue" embed
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{song.name}**",
                    color=0xFFD700  # Secondary color (gold) for queue messages
                )
                embed.add_field(
                    name="Requested by",
                    value=song.requester.display_name,
                    inline=True
                )
                embed.add_field(
                    name="Duration",
                    value=song.formatted_duration,
                    inline=True
                )
                embed.add_field(
                    name="Position in queue",
                    value=len(player.queue),
                    inline=True
                )
                if song.requester.avatar:
                    embed.set_thumbnail(url=song.requester.avatar.url)
                
                await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")