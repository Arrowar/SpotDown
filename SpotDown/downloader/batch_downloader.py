# 09.09.2025

import time
import signal
import logging
import threading
from queue import Queue
from typing import List, Dict


# External imports
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console


# Internal utils
from SpotDown.utils.config_json import config_manager
from SpotDown.extractor.youtube_extractor import YouTubeExtractor
from SpotDown.downloader.youtube_downloader import YouTubeDownloader


# Variable
shutdown_requested = False
workers = config_manager.get("DOWNLOAD", "thread")


def _signal_handler(sig, frame):
    global shutdown_requested
    shutdown_requested = True

signal.signal(signal.SIGINT, _signal_handler)


class WorkerStatus:
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.status = "idle"
        self.current = ""
        self.progress = 0
        self.lock = threading.Lock()

    def update(self, status: str = None, current: str = None, progress: int = None):
        with self.lock:
            if status is not None:
                self.status = status
            if current is not None:
                self.current = current
            if progress is not None:
                self.progress = progress

class BatchDownloader:
    def __init__(self, tracks: List[Dict]):
        self.console = Console()
        self.tracks = tracks
        self.total = len(tracks)
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        self.worker_statuses = [WorkerStatus(i+1) for i in range(workers)]
        self.tasks = Queue()

        for track in tracks:
            self.tasks.put(track)

        self.youtube_extractor = YouTubeExtractor()
        self.downloader = YouTubeDownloader()

    def worker(self, ws: WorkerStatus):
        while not self.tasks.empty():
            if shutdown_requested:
                break

            track = self.tasks.get()
            info = {
                'artist': track.get('artist', ''),
                'title': track.get('title', ''),
                'duration_seconds': int(track.get('duration_ms', 0)) // 1000 if track.get('duration_ms') else None
            }

            # Searching
            ws.update(status="search", current=f"{info['artist']} - {info['title']}", progress=10)
            results = self.youtube_extractor.search_videos(f"{info['artist']} {info['title']}")
            if not results:
                ws.update(status="failed", progress=100)
                self.failed += 1
                self.tasks.task_done()
                continue

            # Downloading
            video = results[0]
            ws.update(status="download", current=video['title'], progress=50)
            success = self.downloader.download(video, track)

            if success:
                ws.update(status="completed", progress=100)
                self.completed += 1
            else:
                ws.update(status="failed", progress=100)
                self.failed += 1

            self.tasks.task_done()

        ws.update(status="idle", current="", progress=0)

    def render(self):
        table = Table()
        table.add_column("Worker")
        table.add_column("Status")
        table.add_column("Progress")
        table.add_column("Current")

        icons = {
            'search': 'Search YT',
            'download': 'Download MP3',
            'completed': 'Completed',
            'failed': 'Failed',
            'idle': 'Idle'
        }

        status_styles = {
            'search': 'bold blue',
            'download': 'bold yellow',
            'completed': 'bold green',
            'failed': 'bold red',
            'idle': 'dim'
        }

        for ws in self.worker_statuses:
            icon = icons.get(ws.status, ws.status)
            style = status_styles.get(ws.status, '')
            status_text = f"[{style}]{icon}[/{style}]" if style else icon
            progress_text = f"[cyan]{ws.progress}%[/cyan]"
            current_text = f"[magenta]{ws.current}[/magenta]"

            table.add_row(
                f"[bold magenta]Worker-{ws.worker_id}[/bold magenta]", 
                status_text, 
                progress_text, 
                current_text
            )

        elapsed = max(time.time() - self.start_time, 0.001)
        done = self.completed + self.failed + self.skipped
        rate = done / elapsed * 60
        remaining = self.total - done
        eta = remaining / (done / elapsed) if done > 0 else float('inf')
        stats = f"📊 {done}/{self.total} ({done/self.total*100:.1f}%) | ✅ {self.completed} | ❌ {self.failed} | ⏭️ {self.skipped} | Rate: {rate:.1f}/min | ETA: {eta/60:.1f}min"

        panel = Panel(stats, title="Progress Stats")
        layout = Table.grid()
        layout.add_row(panel)
        layout.add_row(table)

        return layout

    def run(self):
        global shutdown_requested
        
        # suppress logging to avoid breaking live UI
        logging.disable(logging.CRITICAL)
        threads = []

        for ws in self.worker_statuses:
            t = threading.Thread(target=self.worker, args=(ws,))
            threads.append(t)
            t.start()

        with Live(self.render(), refresh_per_second=1, console=self.console) as live:
            try:
                while any(t.is_alive() for t in threads) and not shutdown_requested:
                    live.update(self.render())
                    time.sleep(0.2)
            except KeyboardInterrupt:
                shutdown_requested = True
            finally:
                live.update(self.render())
                
        for t in threads:
            t.join()