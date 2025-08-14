import os
import json
from pathlib import Path
from typing import Dict, Any


def load_config(env: str = "development") -> Dict[str, Any]:
    """Load configuration from JSON files based on environment"""
    config_dir = Path("config")
    config_files = [config_dir / "config.json", config_dir / f"{env}.json"]

    merged_config = {}

    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                    merged_config.update(config_data)
            except json.JSONDecodeError:
                continue

    # Apply environment variable overrides
    env_config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "api_url": os.getenv("API_URL"),
        "memory_db": os.getenv("MEMORY_DB"),
        "pg_uri": os.getenv("PG_URI"),
    }

    # Filter out None values
    env_config = {k: v for k, v in env_config.items() if v is not None}
    merged_config.update(env_config)

    return merged_config


def get_server_config() -> Dict[str, Any]:
    """Get server configuration with environment detection"""
    env = os.getenv("DULAYNI_ENV", "development")
    return load_config(env)
