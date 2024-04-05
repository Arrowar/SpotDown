# 05.04.2024

import os
import json
import logging
from typing import Dict, List, Optional


# External imports
from rich.console import Console
from playwright.sync_api import sync_playwright


# Internal utils
from SpotDown.utils.headers import get_userAgent
from SpotDown.utils.config_json import config_manager


# Variable
console = Console()
headless = config_manager.get("BROWSER", "headless")
timeout = config_manager.get("BROWSER", "timeout")


class SpotifyExtractor:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.user_agent = get_userAgent()
        self.total_songs = None
        self.playlist_items = []
        logging.info("SpotifyExtractor initialized")

    def __enter__(self):
        """Context manager to automatically handle the browser"""
        logging.info("Starting Playwright and launching browser")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent=self.user_agent, viewport={'width': 1280, 'height': 800}, ignore_https_errors=True
        )
        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically closes the browser"""
        logging.info("Closing browser and stopping Playwright")
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def extract_track_info(self, spotify_url: str, save_json: bool = False) -> Optional[Dict]:
        """
        Extracts track information from a Spotify URL
        
        Args:
            spotify_url (str): Spotify URL of the track
            save_json (bool): If True, saves the raw Spotify API JSON response in the 'log' folder
            
        Returns:
            Dict: Track information or None if an error occurs
        """
        try:
            logging.info(f"Analyzing Spotify URL: {spotify_url}")
            console.print("[cyan]Analyzing Spotify URL ...")
            
            # Extract Spotify data by intercepting API calls
            spotify_data, raw_json = self._extract_spotify_data(spotify_url, return_raw=True)

            if not spotify_data:
                logging.info("Unable to extract data from Spotify")
                console.print("[cyan]Unable to extract data from Spotify")
                return None

            # Save the JSON response if requested
            if save_json and raw_json:
                try:
                    logging.info("Saving Spotify API response JSON")
                    log_dir = os.path.join(os.getcwd(), "log")
                    os.makedirs(log_dir, exist_ok=True)

                    # Use title and artist for the filename if available
                    filename = "spotify_response.json"

                    if spotify_data.get("artist") and spotify_data.get("title"):
                        safe_artist = "".join(c for c in spotify_data["artist"] if c.isalnum() or c in " _-")
                        safe_title = "".join(c for c in spotify_data["title"] if c.isalnum() or c in " _-")
                        filename = f"{safe_artist} - {safe_title}.json"

                    filepath = os.path.join(log_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(raw_json, f, ensure_ascii=False, indent=2)

                    console.print(f"[green]Spotify API response saved to {filepath}")

                except Exception as e:
                    logging.error(f"Could not save JSON file: {e}")
                    console.print(f"[yellow]Warning: Could not save JSON file: {e}")

            logging.info(f"Found track: {spotify_data['artist']} - {spotify_data['title']}")
            console.print(f"[cyan]Found: [red]{spotify_data['artist']} - {spotify_data['title']}[/red]")
            return spotify_data

        except Exception as e:
            logging.error(f"Spotify extraction error: {e}")
            console.print(f"[cyan]Spotify extraction error: {e}")
            return None

    def _extract_spotify_data(self, spotify_url: str, return_raw: bool = False) -> Optional[Dict]:
        """Extracts Spotify data by intercepting API calls"""
        try:
            logging.info(f"Intercepting API calls for URL: {spotify_url}")
            api_responses = []
            
            def handle_request(request):
                if (request.method == "POST" and "/pathfinder/v2/query" in request.url):
                    try:
                        response = request.response()
                        if response and response.status == 200:
                            try:
                                response_data = response.json()
                                
                                if self._is_valid_track_data(response_data):
                                    api_responses.append(response_data)
                                    console.print("[green]Valid API response found")

                            except Exception as e:
                                logging.warning(f"Error parsing API response: {e}")

                    except Exception as e:
                        logging.warning(f"Error accessing response: {e}")

            self.page.on("requestfinished", handle_request)
            self.page.goto(spotify_url)
            
            # Poll every 100ms, stop waiting as soon as a valid response is found or after 10 seconds
            # This avoids unnecessary waiting after a valid API response is received
            for _ in range(timeout * 10):  # 100 * 100ms = 10000ms (10 seconds max)
                if api_responses:
                    logging.info("Valid API response found, stopping polling")
                    break

                self.page.wait_for_timeout(timeout * 10)

            if not api_responses:
                logging.info("No valid API responses found")
                console.print("[cyan]No valid API responses found")
                return (None, None) if return_raw else None

            # Selects the most complete response
            best_response = max(api_responses, key=lambda x: len(json.dumps(x)))
            parsed = self._parse_spotify_response(best_response)
            logging.info("Returning parsed Spotify API response")
            return (parsed, best_response) if return_raw else parsed

        except Exception as e:
            logging.error(f"Spotify data extraction error: {e}")
            console.print(f"[cyan]❌ Spotify data extraction error: {e}")
            return (None, None) if return_raw else None

    def _is_valid_track_data(self, data: Dict) -> bool:
        """Checks if the data contains valid track information"""
        try:
            track_union = data.get("data", {}).get("trackUnion", {})
            return bool(track_union.get("name") and track_union.get("firstArtist", {}).get("items"))
        
        except Exception:
            logging.error("Error validating track data")
            return False

    def _parse_spotify_response(self, response: Dict) -> Dict:
        """Parses the Spotify API response"""
        try:
            # Extract title
            track_data = response.get("data", {}).get("trackUnion", {})
            title = track_data.get("name", "").strip()
            
            # Extract artist
            artist_items = track_data.get("firstArtist", {}).get("items", [])
            artist = artist_items[0].get("profile", {}).get("name", "") if artist_items else ""
            
            # Extract album
            album_data = track_data.get("albumOfTrack", {})
            album = album_data.get("name", "")
            
            # Extract year
            release_date = album_data.get("date", {})
            year = release_date.get("year") if release_date else None
            
            # Extract duration
            duration_ms = track_data.get("duration", {}).get("totalMilliseconds")
            duration_seconds = duration_ms // 1000 if duration_ms else None
            duration_formatted = self._format_seconds(duration_seconds) if duration_seconds else None
            
            # Extract cover art
            cover_url = ""
            cover_sources = album_data.get("coverArt", {}).get("sources", [])

            if cover_sources:
                largest = max(
                    cover_sources,
                    key=lambda x: max(x.get("width", 0), x.get("height", 0))
                )
                cover_url = largest.get("url", "")

            return {
                'title': title,
                'artist': artist,
                'album': album,
                'year': year,
                'duration_seconds': duration_seconds,
                'duration_formatted': duration_formatted,
                'cover_url': cover_url
            }

        except Exception as e:
            logging.error(f"Error parsing Spotify response: {e}")
            console.print(f"[cyan]Error parsing Spotify response: {e}")
            return {}

    def _format_seconds(self, seconds: int) -> str:
        """Formats seconds into mm:ss or hh:mm:ss"""
        if seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
        
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"

    def extract_playlist_tracks(self, playlist_url: str) -> List[Dict]:
        """Extracts all tracks from a Spotify playlist URL"""
        logging.info(f"Extracting playlist tracks from: {playlist_url}")
        self.total_songs = None
        self.playlist_items = []
        console.print("[cyan]Extracting playlist tracks...")

        try:
            def handle_request(response):
                try:
                    if "pathfinder/v2/query" in response.url and response.request.method == "POST":
                        json_data = response.json()
                        if (
                            "data" in json_data and
                            "playlistV2" in json_data["data"] and
                            "content" in json_data["data"]["playlistV2"]
                        ):
                            if self.total_songs is None:
                                self.total_songs = json_data["data"]["playlistV2"]["content"].get("totalCount", 0)
                            items = json_data["data"]["playlistV2"]["content"].get("items", [])
                            for item in items:
                                parsed_item = self._parse_spotify_playlist_item(item)
                                if parsed_item:
                                    self.playlist_items.append(parsed_item)
                except Exception as e:
                    logging.error(f"Error processing playlist request: {e}")
                    console.print(f"Error processing request: {e}")

            self.page.on("response", handle_request)
            self.page.goto(playlist_url)
            self.page.wait_for_timeout(5000)

            if self.total_songs is None:
                logging.error("Could not extract the total number of songs")
                console.print("Error: Could not extract the total number of songs.")
                return []

            logging.info(f"Playlist has {self.total_songs} tracks")
            console.print(f"[cyan]The playlist has [green]{self.total_songs}[/green] tracks")

            try:
                self.page.wait_for_selector('div[data-testid="playlist-tracklist"]', timeout=15000)
            except Exception:
                logging.error("Playlist table did not load")
                console.print("Error: Playlist table did not load")
                return []

            last_item_count = len(self.playlist_items)
            with console.status("[cyan]Loading tracks...") as status:
                while len(self.playlist_items) < self.total_songs:
                    status.update(f"[cyan]Progress: {len(self.playlist_items)}/{self.total_songs} tracks loaded")
                    rows = self.page.locator('div[role="row"]')
                    row_count = rows.count()
                    last_row = rows.nth(row_count - 1)
                    last_row.scroll_into_view_if_needed()
                    current_items = len(self.playlist_items)
                    if current_items > last_item_count:
                        last_item_count = current_items
                    self.page.wait_for_timeout(300)

            # Remove duplicates based on title and artist
            unique = {}
            for item in self.playlist_items:
                key = (item.get("title", ""), item.get("artist", ""))
                if key not in unique:
                    unique[key] = item
            
            unique_tracks = list(unique.values())
            logging.info(f"Extracted {len(unique_tracks)} unique tracks from playlist")
            return unique_tracks

        except Exception as e:
            logging.error(f"Error extracting playlist: {e}")
            console.print(f"Error extracting playlist: {e}")
            return []

    def _parse_spotify_playlist_item(self, item: Dict) -> Dict:
        """Parses a single playlist item from Spotify API response"""
        try:
            # Extract added date
            added_at = item.get("addedAt", {}).get("isoString", "")
            
            # Extract track data
            track_data = item.get("itemV2", {}).get("data", {})
            
            # Extract album name
            album_data = track_data.get("albumOfTrack", {})
            album_name = album_data.get("name", "")
            
            # Extract cover art URL
            cover_art = album_data.get("coverArt", {}).get("sources", [{}])[0].get("url", "")
            
            # Extract artist name
            artist_items = album_data.get("artists", {}).get("items", [])
            artist_name = artist_items[0].get("profile", {}).get("name", "") if artist_items else ""
            
            # Extract track title
            track_title = track_data.get("name", "")
            
            # Extract duration in ms
            duration_ms = track_data.get("trackDuration", {}).get("totalMilliseconds", 0)
            
            # Extract play count
            play_count = track_data.get("playcount", 0)
            
            return {
                "title": track_title,
                "artist": artist_name,
                "album": album_name,
                "added_at": added_at,
                "cover_art": cover_art,
                "duration_ms": duration_ms,
                "play_count": play_count
            }
        
        except Exception as e:
            logging.error(f"Error parsing playlist item: {e}")
            console.print(f"Error parsing playlist item: {e}")
            return {}