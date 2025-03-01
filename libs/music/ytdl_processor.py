import os
import yt_dlp
import multiprocessing
from multiprocessing import Process, Queue

# Base options for both streaming and downloading
base_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'cookiefile': '../cookies.txt',
    'geo_bypass': True,
    'nocheckcertificate': True,
    'extractor_retries': 3,
    'socket_timeout': 15,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
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

def ytdl_process(query, result_queue, mode="stream"):
    """
    Process function that runs in a separate process to handle YouTube operations
    
    Args:
        query: YouTube search query or URL
        result_queue: Queue to store results
        mode: "stream" or "download"
    """
    try:
        # Select appropriate options
        opts = stream_opts if mode == "stream" else download_opts
        
        # Initialize YoutubeDL with options
        ydl = yt_dlp.YoutubeDL(opts)
        
        # Extract info (and download if mode is download)
        data = ydl.extract_info(query, download=(mode == "download"))
        
        # Handle playlist results
        if 'entries' in data:
            data = data['entries'][0]
        
        # Prepare result based on mode
        if mode == "stream":
            result = {
                'success': True,
                'mode': 'stream',
                'title': data.get('title', 'Unknown'),
                'url': data.get('url'),
                'duration': int(data.get('duration', 0)),
                'thumbnail': data.get('thumbnail'),
                'webpage_url': data.get('webpage_url')
            }
        else:  # download mode
            # Get the filename that yt-dlp prepared
            filename = ydl.prepare_filename(data)
            result = {
                'success': True,
                'mode': 'download',
                'title': data.get('title', 'Unknown'),
                'filename': filename,
                'duration': int(data.get('duration', 0)),
                'thumbnail': data.get('thumbnail'),
                'webpage_url': data.get('webpage_url')
            }
        
        # Put result in queue
        result_queue.put(result)
        
    except Exception as e:
        # Handle errors
        result_queue.put({
            'success': False,
            'mode': mode,
            'error': str(e)
        })

class YTDLProcessor:
    """Manager class for YTDL multiprocessing operations"""
    
    def __init__(self, max_processes=2):
        """
        Initialize with process pool limits
        
        Args:
            max_processes: Maximum number of concurrent YTDL processes
        """
        self.max_processes = max_processes
        self.active_processes = {}
        self.result_queues = {}
        
        # Ensure multiprocessing works properly on all platforms
        multiprocessing.set_start_method('spawn', force=True)
    
    def process_url(self, query_id, query, mode="stream"):
        """
        Start processing a YouTube URL or search query in a separate process
        
        Args:
            query_id: Unique identifier for this query (e.g., message ID)
            query: YouTube search query or URL
            mode: "stream" or "download"
            
        Returns:
            None (processing happens asynchronously)
        """
        # Create result queue for this request
        result_queue = Queue()
        self.result_queues[query_id] = result_queue
        
        # Prepare search query if needed (not a direct URL)
        if not query.startswith(('http://', 'https://')):
            query = f"ytsearch:{query}"
        
        # Create and start process
        process = Process(
            target=ytdl_process,
            args=(query, result_queue, mode)
        )
        process.daemon = True  # Process will be terminated when main process exits
        process.start()
        
        # Store process reference
        self.active_processes[query_id] = process
    
    def get_result(self, query_id, timeout=None):
        """
        Get result for a query, if available
        
        Args:
            query_id: Unique identifier used when starting the process
            timeout: How long to wait for result (None = wait forever)
            
        Returns:
            Result dict if available, None if timeout or not found
        """
        if query_id not in self.result_queues:
            return None
            
        queue = self.result_queues[query_id]
        
        try:
            # Try to get result from queue
            result = queue.get(block=True, timeout=timeout)
            
            # Clean up resources
            self._cleanup_resources(query_id)
            
            return result
        except Exception:
            # Timeout or queue error
            return None
    
    def is_processing(self, query_id):
        """Check if a query is still processing"""
        if query_id in self.active_processes:
            process = self.active_processes[query_id]
            return process.is_alive()
        return False
    
    def _cleanup_resources(self, query_id):
        """Clean up resources for a completed query"""
        # Remove queue
        if query_id in self.result_queues:
            del self.result_queues[query_id]
        
        # Remove process reference
        if query_id in self.active_processes:
            del self.active_processes[query_id]
    
    def cancel_process(self, query_id):
        """Cancel a running process"""
        if query_id in self.active_processes:
            process = self.active_processes[query_id]
            if process.is_alive():
                process.terminate()
            self._cleanup_resources(query_id)
            return True
        return False
    
    def cleanup_all(self):
        """Terminate all active processes and clean up resources"""
        for query_id, process in list(self.active_processes.items()):
            if process.is_alive():
                process.terminate()
            self._cleanup_resources(query_id)