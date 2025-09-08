# 05.04.2024

import logging
import subprocess
from typing import Dict


# External imports
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


# Internal utils
from SpotDown.utils.os import file_utils
from SpotDown.utils.config_json import config_manager
from SpotDown.helpers.ffmpeg import convert_to_jpg_with_ffmpeg


# Variable
console = Console()
quality = config_manager.get("DOWNLOAD", "quality")


class YouTubeDownloader:
    def download(self, video_info: Dict, spotify_info: Dict) -> bool:
        """
        Download YouTube video as mp3 320kbps

        Args:
            video_info (Dict): YouTube video info
            spotify_info (Dict): Spotify track info

        Returns:
            bool: True if download succeeded
        """
        try:
            music_folder = file_utils.get_music_folder()
            filename = file_utils.create_filename(
                spotify_info.get('artist', 'Unknown Artist'),
                spotify_info.get('title', video_info.get('title', 'Unknown Title'))
            )
            output_path = music_folder / f"{filename}.%(ext)s"
            logging.info(f"Start download: {video_info.get('url')} as {output_path}")

            # Download cover image if available
            cover_path = None
            cover_url = spotify_info.get('cover_url')
            if cover_url:
                try:
                    cover_path = music_folder / f"{filename}_cover.jpg"
                    with httpx.Client(timeout=10) as client:
                        resp = client.get(cover_url)
                        if resp.status_code == 200:
                            
                            # Check if it's WebP or needs conversion
                            content_type = resp.headers.get("content-type", "").lower()
                            is_webp = content_type.endswith("webp") or cover_url.lower().endswith(".webp")
                            
                            if is_webp or not content_type.startswith("image/jpeg"):
                                
                                # Use ffmpeg for conversion to JPG
                                if convert_to_jpg_with_ffmpeg(resp.content, cover_path):
                                    console.print(f"[blue]Downloaded and converted thumbnail: {cover_path}[/blue]")
                                    logging.info(f"Downloaded and converted thumbnail: {cover_path}")
                                else:
                                    cover_path = None
                                    logging.warning("Failed to convert image with ffmpeg")

                            else:
                                # Direct save for JPG images
                                with open(cover_path, 'wb') as f:
                                    f.write(resp.content)

                                console.print(f"[blue]Downloaded thumbnail: {cover_path}[/blue]")
                                logging.info(f"Downloaded thumbnail: {cover_path}")

                        else:
                            cover_path = None
                            logging.warning(f"Failed to download cover image, status code: {resp.status_code}")
                            
                except Exception as e:
                    console.print(f"[yellow]Unable to download cover: {e}[/yellow]")
                    logging.error(f"Unable to download cover: {e}")
                    cover_path = None

            ytdlp_options = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', quality,
                '--output', str(output_path),
                '--no-playlist',
                '--embed-metadata',
                '--add-metadata',
                '--ffmpeg-location', file_utils.ffmpeg_path
            ]
            
            if cover_path and cover_path.exists():
                ytdlp_options += ['--embed-thumbnail']
            ytdlp_options.append(video_info['url'])

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Downloading...", total=None)
                logging.info(f"Running yt-dlp with options: {ytdlp_options}")
                process = subprocess.run(
                    ytdlp_options,
                    capture_output=True,
                    text=True
                )
                progress.remove_task(task)

            if process.returncode == 0:
                logging.info("yt-dlp finished successfully")

                # Find the downloaded file
                downloaded_files = list(music_folder.glob(f"{filename}.*"))
                if downloaded_files:
                    console.print("[red]Download completed![/red]")
                    logging.info(f"Download completed: {downloaded_files[0]}")

                    # Remove cover file after embedding
                    if cover_path and cover_path.exists():
                        try:
                            cover_path.unlink()
                            logging.info(f"Removed temporary cover file: {cover_path}")

                        except Exception as ex:
                            logging.warning(f"Failed to remove cover file: {ex}")

                    return True
                
                else:
                    console.print("[yellow]Download apparently succeeded but file not found[/yellow]")
                    logging.error("Download apparently succeeded but file not found")
                    return False
            
            else:
                console.print("[red]Download error:[/red]")
                console.print(f"[red]{process.stderr}[/red]")
                logging.error(f"yt-dlp error: {process.stderr}")
                return False

        except Exception as e:
            console.print(f"[red]Error during download: {e}[/red]")
            logging.error(f"Error during download: {e}")
            return False