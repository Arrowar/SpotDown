# 05.04.2024

import time
from typing import Dict, List, Optional


# Internal utils
from SpotDown.utils.logger import Logger
from SpotDown.utils.file_utils import file_utils
from SpotDown.utils.console_utils import ConsoleUtils
from SpotDown.upload.update import update as git_update
from SpotDown.extractor.spotify_extractor import SpotifyExtractor
from SpotDown.extractor.youtube_extractor import YouTubeExtractor
from SpotDown.downloader.youtube_downloader import YouTubeDownloader



# Variable
console = ConsoleUtils()


def extract_spotify_data(spotify_url: str, max_retry: int = 3) -> Optional[Dict]:
    """Extract data from Spotify URL with retry mechanism"""
    for attempt in range(1, max_retry + 1):
        with SpotifyExtractor() as spotify_extractor:
            spotify_info = spotify_extractor.extract_track_info(spotify_url)
        if spotify_info:
            return spotify_info
        elif attempt < max_retry:
            console.show_warning(f"Can't extract data from Spotify. Retrying ({attempt}/{max_retry})...")
            time.sleep(1)
    return None


def search_on_youtube(query: str, max_results: int, duration_seconds: Optional[int] = None) -> List[Dict]:
    """Search for videos on YouTube and sort them by relevance"""
    with YouTubeExtractor() as youtube_extractor:
        results = youtube_extractor.search_videos(query, max_results)
        if results and duration_seconds:
            youtube_extractor.sort_by_affinity_and_duration(results, {'duration_seconds': duration_seconds})
        return results


def download_track(video_info: Dict, spotify_info: Dict) -> bool:
    """Download a single track and add metadata"""
    downloader = YouTubeDownloader()
    music_folder = downloader.file_utils.get_music_folder()
    filename = downloader.file_utils.create_filename(
        spotify_info['artist'],
        spotify_info['title']
    )
    console.show_download_info(music_folder, filename)
    console.show_download_start(video_info['title'], video_info['url'])
    return downloader.download(video_info, spotify_info)


def handle_playlist_download(tracks: List[Dict], max_results: int):
    """Handle downloading all tracks from a playlist"""
    for idx, track in enumerate(tracks, 1):
        console.start_message()
        console.show_info(f"[purple]Downloading track [red]{idx}/{len(tracks)}[/red]: [yellow]{track['artist']} - {track['title']}[/yellow]")

        spotify_info = {
            'artist': track.get('artist', ''),
            'title': track.get('title', ''),
            'album': track.get('album', ''),
            'duration_seconds': int(track.get('duration_ms', 0)) // 1000 if track.get('duration_ms') else None,
            'cover_url': track.get('cover_art', '')
        }

        query = f"{spotify_info['artist']} {spotify_info['title']}"
        youtube_results = search_on_youtube(query, max_results, spotify_info.get('duration_seconds'))

        if not youtube_results:
            console.show_error(f"No YouTube results for {spotify_info['artist']} - {spotify_info['title']}")
            continue

        success = download_track(youtube_results[0], spotify_info)
        if not success:
            console.show_error(f"Error downloading {spotify_info['artist']} - {spotify_info['title']}")


def handle_single_track_download(spotify_info: Dict, max_results: int):
    """Handle downloading a single track"""
    query = f"{spotify_info['artist']} {spotify_info['title']}"
    youtube_results = search_on_youtube(query, max_results, spotify_info.get('duration_seconds'))

    if not youtube_results:
        console.show_error("No YouTube results found.")
        return

    console.display_youtube_results(youtube_results)
    console.show_download_menu(len(youtube_results))

    choice = console.get_download_choice(len(youtube_results))
    if choice == 0:
        console.show_warning("Exit without downloading.")
        return

    selected_video = youtube_results[choice - 1]
    success = download_track(selected_video, spotify_info)
    if not success:
        console.show_error("Error during download.")


def run():
    """Main execution function"""
    Logger()

    console = ConsoleUtils()
    console.start_message()
    git_update()
    file_utils.get_system_summary()

    spotify_url = console.get_spotify_url()
    max_results = 5

    if "/playlist/" in spotify_url:
        with SpotifyExtractor() as spotify_extractor:
            tracks = spotify_extractor.extract_playlist_tracks(spotify_url)
        if not tracks:
            console.show_error("No tracks found in playlist.")
            return
        console.show_info(f"Found [green]{len(tracks)}[/green] tracks in playlist.")
        handle_playlist_download(tracks, max_results)
        return

    spotify_info = extract_spotify_data(spotify_url)
    if not spotify_info:
        console.show_error("Can't extract data from Spotify.")
        return

    time.sleep(1)
    console.start_message()
    console.display_spotify_info(spotify_info)

    handle_single_track_download(spotify_info, max_results)