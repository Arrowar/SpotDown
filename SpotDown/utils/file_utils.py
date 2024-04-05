# 05.04.2024

import re
from pathlib import Path
from typing import Optional


# External imports
from unidecode import unidecode


class FileUtils:

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