# 05.04.2024

import re
import os
import sys
import glob
from pathlib import Path
from typing import Optional
import platform


# External imports
from rich.console import Console
from unidecode import unidecode


# Internal logic
from .ffmpeg_installer import check_ffmpeg


# Variable
console = Console()


class FileUtils:
    ffmpeg_path = None
    ffprobe_path = None

    @staticmethod
    def get_music_folder() -> Path:
        """
        Gets the path to the Music folder.
        
        Returns:
            Path: Path to the Music folder
        """
        music_folder = Path.home() / "Music"
        if not music_folder.exists():

            # If "Music" does not exist, check for Italian "Musica" and rename it to "Music"
            musica_folder = Path.home() / "Musica"
            if musica_folder.exists():
                musica_folder.rename(music_folder)
            else:
                music_folder.mkdir(exist_ok=True)

        return music_folder
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Cleans the filename of invalid characters and applies transliteration.
        
        Args:
            filename (str): Filename to clean
            
        Returns:
            str: Cleaned filename
        """
        # Transliterate to ASCII
        filename = unidecode(filename)
        
        # Remove/replace invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Remove multiple spaces and trim
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename
    
    @staticmethod
    def create_filename(artist: str, title: str, extension: str = "mp3") -> str:
        """
        Creates a filename in the format: Artist - Title.extension
        
        Args:
            artist (str): Artist name
            title (str): Song title
            extension (str): File extension
            
        Returns:
            str: Formatted filename
        """
        clean_artist = FileUtils.sanitize_filename(artist)
        clean_title = FileUtils.sanitize_filename(title)
        
        # Create format: Artist - Title
        filename = f"{clean_artist} - {clean_title}"
        
        return filename
    
    @staticmethod
    def get_download_path(artist: str, title: str) -> Path:
        """
        Gets the full path for the download.
        
        Args:
            artist (str): Artist name
            title (str): Song title
            
        Returns:
            Path: Full file path
        """
        music_folder = FileUtils.get_music_folder()
        filename = FileUtils.create_filename(artist, title)

        return music_folder / filename
    
    @staticmethod
    def file_exists(filepath: Path) -> bool:
        """
        Checks if a file exists.
        
        Args:
            filepath (Path): File path
            
        Returns:
            bool: True if the file exists
        """
        return filepath.exists()
    
    @staticmethod
    def find_downloaded_file(base_path: Path, pattern: str) -> Optional[Path]:
        """
        Finds a downloaded file using a pattern.
        
        Args:
            base_path (Path): Base folder for the search
            pattern (str): Search pattern
            
        Returns:
            Path: First file found or None
        """
        try:
            files = list(base_path.glob(pattern))
            return files[0] if files else None
        
        except Exception:
            return None
    
    @staticmethod
    def get_binary_directory():
        """Get the binary directory based on OS."""
        system = platform.system().lower()
        home = os.path.expanduser('~')

        if system == 'windows':
            return os.path.join(os.path.splitdrive(home)[0] + os.path.sep, 'binary')
        elif system == 'darwin':
            return os.path.join(home, 'Applications', 'binary')
        else:  # linux
            return os.path.join(home, '.local', 'bin', 'binary')
        
    @staticmethod
    def get_ffmpeg_path():
        """Returns the path of FFmpeg."""
        return FileUtils.ffmpeg_path

    @staticmethod
    def get_ffprobe_path():
        """Returns the path of FFprobe."""
        return FileUtils.ffprobe_path
    
    @staticmethod
    def check_python_version():
        """
        Check if the installed Python is the official CPython distribution.
        Exits with a message if not the official version.
        """
        python_implementation = platform.python_implementation()
        python_version = platform.python_version()

        if python_implementation != "CPython":
            console.print(f"[bold red]Warning: You are using a non-official Python distribution: {python_implementation}.[/bold red]")
            console.print("Please install the official Python from [bold blue]https://www.python.org[/bold blue] and try again.", style="bold yellow")
            sys.exit(0)

        console.print(f"[cyan]Python version: [bold red]{python_version}[/bold red]")

    @staticmethod
    def get_system_summary():
        FileUtils.check_python_version()

        # FFmpeg detection
        binary_dir = FileUtils.get_binary_directory()
        system = platform.system().lower()
        arch = platform.machine().lower()

        # Map architecture names
        arch_map = {
            'amd64': 'x64',
            'x86_64': 'x64',
            'x64': 'x64',
            'arm64': 'arm64',
            'aarch64': 'arm64',
            'armv7l': 'arm',
            'i386': 'ia32',
            'i686': 'ia32'
        }
        arch = arch_map.get(arch, arch)

        # Check FFmpeg binaries
        if os.path.exists(binary_dir):
            ffmpeg_files = glob.glob(os.path.join(binary_dir, f'*ffmpeg*{arch}*'))
            ffprobe_files = glob.glob(os.path.join(binary_dir, f'*ffprobe*{arch}*'))

            if ffmpeg_files and ffprobe_files:
                FileUtils.ffmpeg_path = ffmpeg_files[0]
                FileUtils.ffprobe_path = ffprobe_files[0]

                if system != 'windows':
                    os.chmod(FileUtils.ffmpeg_path, 0o755)
                    os.chmod(FileUtils.ffprobe_path, 0o755)
            else:
                FileUtils.ffmpeg_path, FileUtils.ffprobe_path, ffplay_path = check_ffmpeg()
        else:
            FileUtils.ffmpeg_path, FileUtils.ffprobe_path, ffplay_path = check_ffmpeg()

        if not FileUtils.ffmpeg_path or not FileUtils.ffprobe_path:
            console.log("[red]Can't locate ffmpeg or ffprobe")
            sys.exit(0)

        ffmpeg_str = f"'{FileUtils.ffmpeg_path}'" if FileUtils.ffmpeg_path else "None"
        ffprobe_str = f"'{FileUtils.ffprobe_path}'" if FileUtils.ffprobe_path else "None"
        console.print(f"[cyan]Path: [red]ffmpeg [bold yellow]{ffmpeg_str}[/bold yellow][white], [red]ffprobe [bold yellow]{ffprobe_str}[/bold yellow][white].")


file_utils = FileUtils()