#!/usr/bin/env python3
"""
Validate that all JSON files under config/*/ are valid JSON.

Usage: python scripts/validate_json_configs.py
"""

import sys
import json
from pathlib import Path
from typing import List

CONFIG_DIR = Path(__file__).parent.parent / "config"


def find_json_files(config_dir: Path) -> List[Path]:
    """
    Recursively find all .json files under config/*/.
    """
    return list(config_dir.glob("*/**/*.json")) + list(config_dir.glob("*/.json"))


def validate_json_file(json_file: Path) -> bool:
    """
    Validate a single JSON file. Returns True if valid, False otherwise.
    """
    try:
        with json_file.open("r", encoding="utf-8") as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"ERROR: {json_file} is not valid JSON: {e}", file=sys.stderr)
        return False


def main() -> None:
    """
    Main entry point for JSON validation script.
    """
    json_files = find_json_files(CONFIG_DIR)
    if not json_files:
        print("No JSON files found under config/*/.")
        sys.exit(0)

    failed = False
    for json_file in json_files:
        if not validate_json_file(json_file):
            failed = True

    if failed:
        print("\nSome JSON files are invalid.")
        sys.exit(1)
    else:
        print("All JSON files are valid.")
        sys.exit(0)


if __name__ == "__main__":
    main() 