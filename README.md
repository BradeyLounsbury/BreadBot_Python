# 🍞 BreadBot

A feature-rich Discord bot for music playback and more. BreadBot allows you to play music from YouTube or local audio files, manage a queue, and interact with users through various commands.

## Features

### 🎵 Music Features
- Stream music directly from YouTube or play local audio files
- Comprehensive queue system with management commands
- Live progress bar showing current playback position
- Support for multiple audio formats (.mp3, .wav, .ogg, .m4a)
- Detailed "Now Playing" embeds with song information

### ⚡ General Features
- Slash commands support for easier interaction
- Auto-response to trigger words (responds with 🍞 when someone says "bread")
- Help command with detailed information about all available commands
- Customizable command prefix (default: `-`)

## Requirements

- Python 3.8 or higher
- Discord.py library (v2.0+)
- yt-dlp for YouTube streaming
- FFmpeg for audio processing
- Additional Python libraries listed in requirements.txt

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/breadbot.git
   cd breadbot
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

4. Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   HELP_CHANNEL_ID=optional_channel_id_for_pinned_help_message
   ```

5. Create an `audio` folder in the root directory for local audio files.

## Running the Bot

Start the bot with:
```
python discord-bot.py
```

## Commands

### Prefix Commands (Default: `-`)

#### Music Commands
- `-play <query>` - Play a song from YouTube or local audio file
- `-pause` - Pause/resume the current song
- `-skip` - Skip to the next song in queue
- `-stop` - Stop playing, clear queue, and disconnect
- `-queue` - Show the current music queue
- `-remove <position>` or `-r <position>` - Remove a song from queue by position number
- `-rl` - Remove the last song in queue

#### General Commands
- `-hello` - Get a friendly greeting
- `-ping` - Check bot latency

### Slash Commands

- `/hello` - Get a friendly greeting from BreadBot
- `/ping` - Check the bot's current latency
- `/help` - Show the help message

## Project Structure

- `discord-bot.py` - Main bot file and entry point
- `prefix_commands/` - Directory containing all prefix-based commands
- `slash_commands/` - Directory containing all slash commands
- `libs/music/` - Core music player functionality
  - `core.py` - MusicPlayer and Song classes
  - `ytdl_processor.py` - YouTube download/streaming processor

## Local Audio Files

To play local audio files:
1. Place your audio files in the `audio/` folder
2. Use the command `-play filename` (without extension)
3. Supported formats: .mp3, .wav, .ogg, .m4a

## YouTube Features

The bot can stream music from YouTube by providing:
- Direct video URLs
- Search terms (will play the first result)

## Troubleshooting

### Common Issues

- **Bot not responding to commands**: Make sure you're using the correct prefix (default: `-`)
- **Music not playing**: Ensure FFmpeg is properly installed and accessible in your PATH
- **YouTube playback issues**: Check your internet connection and ensure yt-dlp is up to date

### Updating yt-dlp

YouTube frequently changes its site, which may break yt-dlp. Update it regularly:
```
pip install -U yt-dlp
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
