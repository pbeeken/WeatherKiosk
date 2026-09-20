from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any

import tools

@dataclass
class CloudDB:
    """Load Grafana Cloud Loki credentials from the local secrets file."""

    LOKI_URL: str   = field(init=False)
    LOKI_USER: str  = field(init=False)  # Placeholder for Grafana Cloud username.
    LOKI_TOKEN_WRTE: str = field(init=False)  # Placeholder for Grafana Cloud API token.
    LOKI_TOKEN_READ: str = field(init=False)  # Placeholder for Grafana Cloud API token.

    def __post_init__(self):
        # We are overriding the checking of the initialization config to load from a local secrets file instead of environment variables.
        init = tools.load_initialization_config(file_path=GCF.BASE_DIR / ".secrets/" / "weather-buoy-capture.json") # type: ignore
        # print("Loaded initialization config:", init)
        # --- Grafana Cloud Loki credentials ---
        self.LOKI_URL  = init.get("cloud_database").get("host")             # type: ignore
        self.LOKI_USER = init.get("cloud_database").get("user")             # type: ignore
        self.LOKI_TOKEN_WRTE = init.get("cloud_database").get("secretWRTE") # type: ignore
        self.LOKI_TOKEN_READ = init.get("cloud_database").get("secretREAD") # type: ignore

CLD = CloudDB()
