<div align="center">

## 📊 Project Status & Info
[![PyPI Version](https://img.shields.io/pypi/v/spotdown?logo=pypi&logoColor=white&labelColor=2d3748&color=3182ce&style=for-the-badge)](https://pypi.org/project/spotdown)
[![Last Commit](https://img.shields.io/github/last-commit/Arrowar/spotdown?logo=git&logoColor=white&labelColor=2d3748&color=805ad5&style=for-the-badge)](https://github.com/Arrowar/spotdown/commits)
[![Issues](https://img.shields.io/github/issues/Arrowar/spotdown?logo=github&logoColor=white&labelColor=2d3748&color=ed8936&style=for-the-badge)](https://github.com/Arrowar/spotdown/issues)
[![License](https://img.shields.io/github/license/Arrowar/spotdown?logo=gnu&logoColor=white&labelColor=2d3748&color=e53e3e&style=for-the-badge)](https://github.com/Arrowar/spotdown/blob/main/LICENSE)

## 💝 Support the Project

[![Donate PayPal](https://img.shields.io/badge/💳_Donate-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white&labelColor=2d3748)](https://www.paypal.com/donate/?hosted_button_id=UXTWMT8P6HE2C)

## 🚀 Download & Install

[![Windows](https://img.shields.io/badge/🪟_Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_win.exe)
[![macOS](https://img.shields.io/badge/🍎_macOS-000000?style=for-the-badge&logo=apple&logoColor=white&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_mac)
[![Linux latest](https://img.shields.io/badge/🐧_Linux_latest-FCC624?style=for-the-badge&logo=linux&logoColor=black&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_linux_latest)
[![Linux 22.04](https://img.shields.io/badge/🐧_Linux_22.04-FCC624?style=for-the-badge&logo=linux&logoColor=black&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_linux_previous)

---

*⚡ **Quick Start:** `pip install spotdown && spotdown`*

</div>

## 📋 Table of Contents

- [✨ Features](#features)
- [🛠️ Installation](#️installation)
- [⚙️ Setup](#setup)
- [⚙️ Configuration](#configuration)
- [💻 Usage](#usage)

## Features

- 🎵 **Download individual songs** from Spotify
- 📋 **Download entire playlists** with ease
- 🔍 **No authentication required** - uses web scraping
- 🎨 **Automatic cover art embedding** (JPEG format)
- ⚡ **Simple command-line interface** - just run `spotdown`!

## Installation

### Method 1: PyPI (Recommended)

```bash
pip install spotdown
```

That's it! You can now run `spotdown` from anywhere in your terminal.

### Method 2: From Source

If you prefer to install from source:

```bash
git clone https://github.com/Arrowar/spotdown.git
cd spotdown
pip install -e .
```

### Prerequisites

The following dependencies will be automatically installed:

- **Python 3.8+**
- **FFmpeg** (for audio processing)
- **yt-dlp** (for downloading)
- **Playwright** (for web scraping)

After installation, run this one-time setup command:

```bash
playwright install chromium
```

## Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in and create a new application
3. Copy your **Client ID** and **Client Secret**
4. Create a file named `.env` in the SpotDown directory with the following content:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
```

5. Save the file. SpotDown will automatically load these credentials.

### Error Handling
- If the credentials are missing, SpotDown will log an error and exit.
- If the credentials are invalid, SpotDown will log an error and exit. Please double-check your `.env` file and credentials.

## Configuration

SpotDown uses a JSON configuration file with the following structure:

```json
{
    "DEFAULT": {
        "clean_console": true,
        "show_message": true
    },
    "DOWNLOAD": {
        "auto_first": false,
        "quality": "320K"
    }
}
```

### Configuration Options

#### DEFAULT Settings
- **`clean_console`**: Clear console output for cleaner interface
- **`show_message`**: Display informational messages during execution

#### DOWNLOAD Settings
- **`auto_first`**: Automatically select first search result
- **`quality`**: Audio quality (320K recommended for best quality)

## Usage

### Starting SpotDown

Simply run the following command in your terminal:

```bash
spotdown
```

The interactive interface will guide you through the download process.

### Download Individual Songs

1. Run `spotdown`
2. Paste the Spotify song URL when prompted
3. The script will automatically:
   - Extract song information
   - Search for the best quality version
   - Download as MP3 with embedded cover art

### Download Playlists

1. Run `spotdown`
2. Paste the Spotify playlist URL when prompted
3. All songs in the playlist will be downloaded automatically

### Example Usage

```bash
$ spotdown
🎵 Welcome to SpotDown!
Please paste your Spotify URL: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
🔍 Processing: Song Name - Artist Name
⬇️ Downloading...
✅ Download complete!
```

## To Do

- [ ] Implement batch download queue
- [ ] Add GUI interface option
- [ ] Support for additional music platforms
- [ ] Album art quality selection
- [ ] Custom output directory configuration

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. 

**Important**: This tool is intended for educational purposes and personal use only. Users are responsible for ensuring they comply with applicable laws and platform terms of service. The developers do not encourage or condone piracy or copyright infringement.

---

<div align="center">

**Made with ❤️ for music lovers**

*If you find this project useful, consider starring it! ⭐*

</div>
