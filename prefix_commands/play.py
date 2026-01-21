import discord
from discord.ext import commands
import os
import asyncio
from functools import partial
import uuid
from libs.music.core import MusicPlayer, Song, StreamSong, players
from libs.music.ytdl_processor import YTDLProcessor

# Create a global YTDLProcessor instance with 2 max processes
ytdl_processor = YTDLProcessor(max_processes=2)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.title = data.get('title', 'Unknown')
        self.url = data.get('url')
        self.duration = int(data.get('duration', 0))
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')
        self.filename = data.get('filename')  # For downloaded files

async def check_ytdl_result(ctx, query_id, status_message, query):
    """
    Check for YTDL process results periodically and update status message
    Returns the YTDLSource when complete or None if failed
    """
    # Set timeout counter (max 60 seconds)
    timeout_counter = 0
    max_timeout = 60
    
    while timeout_counter < max_timeout:
        # Check if result is available
        result = ytdl_processor.get_result(query_id, timeout=0.5)
        
        if result is not None:
            # Process completed
            if result['success']:
                # Success - create appropriate audio source
                if result['mode'] == 'stream':
                    # Update status message
                    embed = discord.Embed(
                        title="✅ Found!",
                        description=f"Playing: **{result['title']}**",
                        color=0x89CFF0
                    )
                    if result.get('thumbnail'):
                        embed.set_thumbnail(url=result['thumbnail'])
                    await status_message.edit(embed=embed)
                    
                    # Create source for streaming
                    source = discord.FFmpegPCMAudio(result['url'])
                    ytdl_source = YTDLSource(source, data=result, volume=0.5)
                    return ytdl_source, True
                else:
                    # Downloaded file
                    embed = discord.Embed(
                        title="✅ Downloaded!",
                        description=f"Playing: **{result['title']}**",
                        color=0x89CFF0
                    )
                    if result.get('thumbnail'):
                        embed.set_thumbnail(url=result['thumbnail'])
                    await status_message.edit(embed=embed)
                    
                    # Get the final filename after post-processing
                    base_filename = os.path.splitext(result['filename'])[0]
                    # Try common extensions (.mp3 first since that's our preferred format)
                    for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                        test_filename = f"{base_filename}{ext}"
                        if os.path.exists(test_filename):
                            source = discord.FFmpegPCMAudio(test_filename)
                            result['filename'] = test_filename  # Update with actual file
                            ytdl_source = YTDLSource(source, data=result, volume=0.5)
                            return ytdl_source, False
                    
                    # If we can't find the processed file, report error
                    await status_message.edit(content="❌ Could not find processed audio file.", embed=None)
                    return None, None
            else:
                # Error occurred
                await status_message.edit(content=f"❌ Error: {result['error']}", embed=None)
                return None, None
        
        # No result yet, update status message every 5 seconds
        if timeout_counter % 5 == 0 and timeout_counter > 0:
            embed = discord.Embed(
                title="🔍 Still searching...",
                description=f"Looking for: **{query}** ({timeout_counter}s)",
                color=0x89CFF0
            )
            await status_message.edit(embed=embed)
        
        # Increment timeout counter
        timeout_counter += 1
        
        # Short sleep to avoid busy waiting
        await asyncio.sleep(1)
    
    # Timed out
    ytdl_processor.cancel_process(query_id)
    await status_message.edit(content="❌ Search timed out after 60 seconds.", embed=None)
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
            # Show searching status
            status_embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: **{query}**",
                color=0x89CFF0
            )
            status_message = await ctx.send(embed=status_embed)
            
            # Generate a unique ID for this request
            query_id = str(uuid.uuid4())
            
            # Start the YTDL process in a separate process
            ytdl_processor.process_url(query_id, query, mode="stream")
            
            # Wait for result (non-blocking)
            source, is_stream = await check_ytdl_result(ctx, query_id, status_message, query)
            
            if not source:
                return  # Error message already shown by check_ytdl_result
            
            # Create StreamSong from YTDLSource
            song = StreamSong(source, ctx.author)
        else:
            # Use regular Song class for local files
            song = Song(actual_filename, full_path, ctx.author)

        try:
            voice_client_connected = False

            # Connect to voice channel if not already connected
            if ctx.voice_client is None:
                await voice_channel.connect()
                voice_client_connected = True
            elif ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
                voice_client_connected = True

            # Add delay after connecting to allow voice connection to stabilize
            if voice_client_connected:
                await asyncio.sleep(1.5)  # Give the voice connection time to establish
            
            # Verify connection is still active
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                await ctx.send("❌ Failed to establish voice connection. Please try again.")
                return

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