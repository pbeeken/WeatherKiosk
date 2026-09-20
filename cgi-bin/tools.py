from typing import Any, Dict
import os
import json
from datetime import datetime
from pathlib import Path

import requests

def grep_pngurl_fromlandingpage(url: str, target_string: str = ".png") -> str | None:
    """UCONN LISICOS has a php page that generates a .png image.  The name of this image changes frequently.
    This function reads the php page and extracts the image name and then returns the generated png URL.
    This is a bit more work but it is more robust to changes in the image name which for exrx is often.

    Args:
        url (str): The URL of the php page to read.
        target_string (str): The string to search for in the php page that flags the .png image name.

    Returns:
        str | None: The generated png URL or None if not found.
    """
    try:
        # Perform the GET request
        response = requests.get(url, timeout=10)  # Set a timeout for the request

        # Raise an exception for HTTP error codes (e.g., 404, 500)
        response.raise_for_status()

        # requests handles string decoding automatically via response.text.
        # splitlines() operates on the decoded text directly.
        pngURL = None
        for line in response.text.splitlines():
            if target_string in line:
                pngURL = line.strip()
                break

        if pngURL:
            for part in pngURL.split('"'):
                if "clydebank" in part:
                    return part
        else:
            print("Target string not found in the URL content.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")

    return None

def load_initialization_config(file_path: str) -> Dict[str, Any]:
    """Reads a JSON configuration file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the JSON initialization file.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration elements.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    # Verify the file exists before attempting to read
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Initialization file not found at: {os.path.abspath(file_path)}"
        )

    # Read and parse the JSON file
    with open(file_path, "r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)

    return config_data

def timestamp_serializer(obj):
    """Converts Pandas/Python timestamps into ISO-8601 strings for JSON."""
    # Check if the object has an isoformat method (works for Pandas Timestamp & datetime)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def timestamp_filename(base_dir: Path, source_url: str) -> Path:
    """Generates a timestamped filename based on the source URL."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return base_dir / "tmp" / (timestamp + "_" + source_url.split("/")[-1])
