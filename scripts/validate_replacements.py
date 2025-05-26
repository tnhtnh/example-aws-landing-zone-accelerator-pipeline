#!/usr/bin/env python3
"""
Validate that all replacement keys used in config/*.yaml are defined in replacements-config.yaml,
and that all keys in replacements-config.yaml are actually referenced in the config files.

Fails if:
- Any referenced key is missing from replacements-config.yaml
- Any key in replacements-config.yaml is not referenced in any config file

Usage: python scripts/validate_replacements.py
"""

import re
import sys
from pathlib import Path
from typing import Set, List
import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config"
REPLACEMENTS_FILE = CONFIG_DIR / "replacements-config.yaml"

RE_KEY_PATTERN = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def extract_replacement_keys_from_yaml_files(config_dir: Path, exclude: List[str]) -> Set[str]:
    """
    Extract all replacement keys (e.g., {{ Key }}) from all YAML files in config_dir except those in exclude.
    Exclusion is robust to path/case differences by using Path.resolve().
    """
    keys: Set[str] = set()
    # Build a set of resolved paths to exclude
    exclude_paths = { (config_dir / fname).resolve() for fname in exclude }
    for yaml_file in config_dir.glob("*.yaml"):
        if yaml_file.resolve() in exclude_paths:
            continue
        try:
            text = yaml_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {yaml_file}: {e}", file=sys.stderr)
            continue
        found = RE_KEY_PATTERN.findall(text)
        keys.update(found)
    return keys


def extract_defined_keys_from_replacements(replacements_file: Path) -> Set[str]:
    """
    Extract all defined keys from replacements-config.yaml (expects a 'globalReplacements' list of dicts with 'key').
    """
    try:
        with replacements_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {replacements_file}: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict) or "globalReplacements" not in data:
        print(f"Error: {replacements_file} does not contain 'globalReplacements' as a list.", file=sys.stderr)
        sys.exit(1)
    replacements = data["globalReplacements"]
    if not isinstance(replacements, list):
        print(f"Error: 'globalReplacements' in {replacements_file} is not a list.", file=sys.stderr)
        sys.exit(1)
    keys = set()
    for entry in replacements:
        if not isinstance(entry, dict) or "key" not in entry:
            print(f"Warning: Skipping invalid entry in 'globalReplacements': {entry}", file=sys.stderr)
            continue
        keys.add(str(entry["key"]))
    return keys


def main() -> None:
    """
    Main entry point for validation script.
    """
    referenced_keys = extract_replacement_keys_from_yaml_files(CONFIG_DIR, exclude=[REPLACEMENTS_FILE.name])
    defined_keys = extract_defined_keys_from_replacements(REPLACEMENTS_FILE)

    missing_keys = referenced_keys - defined_keys
    unused_keys = defined_keys - referenced_keys

    failed = False
    if missing_keys:
        print("\nERROR: The following replacement keys are referenced in config/*.yaml but NOT defined in replacements-config.yaml:")
        for key in sorted(missing_keys):
            print(f"  - {key}")
        failed = True
    if unused_keys:
        print("\nERROR: The following keys are defined in replacements-config.yaml but NOT referenced in any config/*.yaml:")
        for key in sorted(unused_keys):
            print(f"  - {key}")
        failed = True
    if not failed:
        print("All replacement keys are valid and in sync.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 