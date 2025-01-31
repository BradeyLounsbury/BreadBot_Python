from collections import deque
from datetime import datetime, timedelta
import os
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.m4a import M4A

class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.current_song = None
        self.is_playing = False

    def add_to_queue(self, song):
        self.queue.append(song)

    def get_next_song(self):
        return self.queue.popleft() if self.queue else None

    def clear_queue(self):
        self.queue.clear()
        self.current_song = None

class Song:
    def __init__(self, filename, full_path, requester):
        self.name = filename
        self.full_path = full_path
        self.requester = requester
        self.added_at = datetime.now()
        self.duration = self._get_duration()

    def _get_duration(self):
        """Get the duration of the audio file in seconds"""
        try:
            # Get file extension
            ext = os.path.splitext(self.full_path)[1].lower()
            
            # Handle different audio formats
            if ext == '.mp3':
                audio = MP3(self.full_path)
            elif ext == '.wav':
                audio = WAVE(self.full_path)
            elif ext == '.ogg':
                audio = OggVorbis(self.full_path)
            elif ext == '.m4a':
                audio = M4A(self.full_path)
            else:
                # Fallback to generic file handler
                audio = File(self.full_path)
            
            # Return duration in seconds
            return int(audio.info.length)
        except Exception as e:
            print(f"Error getting duration for {self.name}: {e}")
            return 0

    @property
    def formatted_duration(self):
        """Format duration as mm:ss or hh:mm:ss if over an hour"""
        duration = timedelta(seconds=self.duration)
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

# Shared music player instance for all commands
players = {}