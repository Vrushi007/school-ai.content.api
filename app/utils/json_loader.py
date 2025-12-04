"""
JSON file loader utility for seed data.
"""
import json
from pathlib import Path
from typing import Any, List, Dict


def load_json(file_name: str) -> List[Dict[str, Any]]:
    """
    Load JSON data from seed_data directory.
    
    Args:
        file_name: Name of the JSON file (e.g., "states.json")
    
    Returns:
        List of dictionaries from the JSON file
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    # Get the project root (parent of app directory)
    base_path = Path(__file__).resolve().parent.parent.parent
    file_path = base_path / "seed_data" / file_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {file_name}, got {type(data)}")
    
    return data

