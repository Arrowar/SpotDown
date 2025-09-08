# 08.09.2025

import os
import logging
import tempfile
import subprocess


# Internal utils
from SpotDown.utils.os import file_utils


def convert_to_jpg_with_ffmpeg(input_data: bytes, output_path) -> bool:
    """
    Convert image data to JPG using ffmpeg

    Args:
        input_data (bytes): Raw image data
        output_path: Path where to save the converted JPG

    Returns:
        bool: True if conversion succeeded
    """
    try:
        # Create a temporary file for the input image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_input:
            temp_input.write(input_data)
            temp_input.flush()

            # Use ffmpeg to convert to JPG
            ffmpeg_cmd = [
                str(file_utils.ffmpeg_path),
                '-i', temp_input.name,
                '-q:v', '2',  # High quality JPG
                '-y',  # Overwrite output file
                str(output_path)
            ]

            process = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True
            )

            # Clean up temporary file
            try:
                os.unlink(temp_input.name)
            except Exception:
                pass

            return process.returncode == 0

    except Exception as e:
        logging.error(f"FFmpeg conversion failed: {e}")
        return False