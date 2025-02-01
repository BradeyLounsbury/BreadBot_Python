import discord
from discord.ext import commands
import os
import asyncio
from functools import partial
from youtubesearchpython import VideosSearch
import yt_dlp
from libs.music.core import MusicPlayer, Song, StreamSong, players

# Base options for both streaming and downloading
base_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'cookies': '../cookies.txt'
}

# Streaming-specific options
stream_opts = {
    **base_opts,
    'extract_audio': True,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Download options (used as fallback)
download_opts = {
    **base_opts,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'audio/%(title)s.%(ext)s',
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'Unknown')
        self.url = data.get('url')
        self.duration = int(data.get('duration', 0))
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        opts = stream_opts if stream else download_opts

        ydl = yt_dlp.YoutubeDL(opts)
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ydl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename), data=data)

async def stream_or_download(query, ctx):
    """Attempt to stream, fallback to download if streaming fails"""
    try:
        # First try streaming
        source = await YTDLSource.from_url(f"ytsearch:{query}", stream=True)
        return source, True  # True indicates streaming
    except Exception as e:
        print(f"Streaming failed, falling back to download: {e}")
        try:
            # Fallback to downloading
            source = await YTDLSource.from_url(f"ytsearch:{query}", stream=False)
            return source, False  # False indicates downloaded
        except Exception as e:
            print(f"Download also failed: {e}")
            return None, None

async def update_progress(ctx, player, message):
    """Update the progress bar every 10 seconds"""
    while player.is_playing and player.current_song:
        try:
            # Create updated embed
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{player.current_song.name}**",
                color=0x89CFF0
            )
            
            # Add progress bar
            position = player.get_current_position()
            duration = player.current_song.duration
            progress_bar = player.create_progress_bar()
            
            time_format = lambda s: f"{int(s/60):02d}:{int(s%60):02d}"
            progress_text = f"\n{time_format(position)} {progress_bar} {time_format(duration)}"
            
            embed.add_field(
                name="Progress",
                value=progress_text,
                inline=False
            )
            
            embed.add_field(
                name="Requested by",
                value=player.current_song.requester.display_name,
                inline=True
            )

            if hasattr(player.current_song, 'thumbnail'):
                embed.set_thumbnail(url=player.current_song.thumbnail)
            elif player.current_song.requester.avatar:
                embed.set_thumbnail(url=player.current_song.requester.avatar.url)
            
            await message.edit(embed=embed)
            
            # Wait 10 seconds before next update
            await asyncio.sleep(10)
            
        except discord.NotFound:
            # Message was deleted
            break
        except Exception as e:
            print(f"Error updating progress: {e}")
            break

def after_song_callback(error, ctx, bot):
    """Callback that runs after a song finishes"""
    if error:
        print(f'Player error: {error}')
        return

    # Use create_task to schedule play_next in the event loop
    bot.loop.create_task(play_next(ctx, bot))

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

    # Check if it's a streaming source or local file
    if hasattr(next_song, 'stream_url'):
        audio_source = discord.FFmpegPCMAudio(next_song.stream_url)
    else:
        audio_source = discord.FFmpegPCMAudio(next_song.full_path)
    
    # Create "Now Playing" embed
    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**{next_song.name}**",
        color=0x89CFF0
    )
    # Add initial progress bar
    progress_text = f"\n00:00 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ {next_song.formatted_duration}"
    embed.add_field(
        name="Progress",
        value=progress_text,
        inline=False
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
    if hasattr(next_song, 'thumbnail'):
        embed.set_thumbnail(url=next_song.thumbnail)
    elif next_song.requester.avatar:
        embed.set_thumbnail(url=next_song.requester.avatar.url)
    
    # Send embed and start progress updates
    now_playing_message = await ctx.send(embed=embed)
    player.start_playback()
    
    # Start progress update task
    update_task = bot.loop.create_task(update_progress(ctx, player, now_playing_message))
    player.current_update_task = update_task
    
    # Use functools.partial to pass additional arguments to the callback
    from functools import partial
    callback = partial(after_song_callback, ctx=ctx, bot=bot)
    
    ctx.voice_client.play(audio_source, after=callback)

def setup(bot):
    """Setup the play command"""
    @bot.command(name='play')
    async def play(ctx, *, query: str):
        """Play an audio file or YouTube video in the user's voice channel"""
        if ctx.guild.id not in players:
            players[ctx.guild.id] = MusicPlayer()
        
        player = players[ctx.guild.id]

        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return
            
        # Get the voice channel
        voice_channel = ctx.author.voice.channel
        
        # First, check if it's a local file
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
        
        # Try to find the file with any supported extension
        full_path = None
        actual_filename = None
        is_local = False
        
        for ext in audio_extensions:
            test_path = f"audio/{query}{ext}"
            if os.path.exists(test_path):
                full_path = test_path
                actual_filename = f"{query}{ext}"
                is_local = True
                break
        
        # If not a local file, try streaming from YouTube
        if not is_local:
            status_embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: **{query}**",
                color=0x89CFF0
            )
            status_message = await ctx.send(embed=status_embed)

            source, is_stream = await stream_or_download(query, ctx)
            if not source:
                await status_message.edit(content="❌ Failed to play the requested song.", embed=None)
                return

            # Update status message
            status_embed.title = "✅ Found!"
            status_embed.description = f"Playing: **{source.title}**"
            if source.thumbnail:
                status_embed.set_thumbnail(url=source.thumbnail)
            await status_message.edit(embed=status_embed)

            song = StreamSong(source, ctx.author)
        else:
            # Use regular Song class for local files
            song = Song(actual_filename, full_path, ctx.author)

        try:
            # Connect to voice channel if not already connected
            if ctx.voice_client is None:
                await voice_channel.connect()
            elif ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
            
            if not player.is_playing:
                player.current_song = song
                player.is_playing = True
                
                # Use appropriate audio source
                if is_local:
                    audio_source = discord.FFmpegPCMAudio(full_path)
                else:
                    audio_source = discord.FFmpegPCMAudio(song.stream_url)
                
                # Create "Now Playing" embed
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song.name}**",
                    color=0x89CFF0
                )
                # Add initial progress bar
                progress_text = f"\n00:00 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ {song.formatted_duration}"
                embed.add_field(
                    name="Progress",
                    value=progress_text,
                    inline=False
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
                
                if hasattr(song, 'thumbnail'):
                    embed.set_thumbnail(url=song.thumbnail)
                elif song.requester.avatar:
                    embed.set_thumbnail(url=song.requester.avatar.url)
                
                # Send embed and start progress updates
                now_playing_message = await ctx.send(embed=embed)
                player.start_playback()
                
                # Start progress update task
                update_task = bot.loop.create_task(update_progress(ctx, player, now_playing_message))
                player.current_update_task = update_task
                
                # Use functools.partial to pass additional arguments to the callback
                from functools import partial
                callback = partial(after_song_callback, ctx=ctx, bot=bot)
                
                ctx.voice_client.play(audio_source, after=callback)
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

                if hasattr(song, 'thumbnail'):
                    embed.set_thumbnail(url=song.thumbnail)
                elif song.requester.avatar:
                    embed.set_thumbnail(url=song.requester.avatar.url)
                
                await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")