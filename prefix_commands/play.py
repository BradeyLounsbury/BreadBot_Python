import discord
from discord.ext import commands
import os
import asyncio
from libs.music.core import MusicPlayer, Song, players

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
            
            if player.current_song.requester.avatar:
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
    if next_song.requester.avatar:
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
                if song.requester.avatar:
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
                if song.requester.avatar:
                    embed.set_thumbnail(url=song.requester.avatar.url)
                
                await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")