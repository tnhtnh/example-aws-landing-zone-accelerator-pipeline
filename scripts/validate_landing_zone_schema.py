#!/usr/bin/env python3
"""
Validates Landing Zone Accelerator configuration files against their respective JSON schemas.
"""

import argparse
import json
import os
import sys
import yaml
import requests
import jsonschema

# Configuration mapping between YAML files and their schema URLs
CONFIG_SCHEMAS = {
    "accounts-config.yaml": "accounts-config.json",
    "customizations-config.yaml": "customizations-config.json",
    "global-config.yaml": "global-config.json",
    "iam-config.yaml": "iam-config.json",
    "network-config.yaml": "network-config.json",
    "organization-config.yaml": "organization-config.json",
    "replacements-config.yaml": "replacements-config.json",
    "security-config.yaml": "security-config.json"
}

BASE_URL = "https://raw.githubusercontent.com/awslabs/landing-zone-accelerator-on-aws/{}/source/packages/@aws-accelerator/config/lib/schemas/{}"

def load_yaml_file(file_path):
    """Load YAML file and return its contents."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {str(e)}")
        return None

def fetch_schema(schema_name, version):
    """Fetch JSON schema from GitHub."""
    url = BASE_URL.format(version, schema_name)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schema {url}: {str(e)}")
        return None

def validate_config(config_data, schema_data, config_name):
    """Validate configuration against schema."""
    try:
        jsonschema.validate(instance=config_data, schema=schema_data)
        print(f"✅ {config_name} is valid")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ {config_name} validation error:")
        print(f"   Path: {' > '.join([str(p) for p in e.path])}")
        print(f"   Message: {e.message}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Validate Landing Zone Accelerator configuration files against schemas")
    parser.add_argument("--version", default="main", help="Landing Zone Accelerator version/branch/commit to use for schemas")
    parser.add_argument("--config-dir", default="config", help="Directory containing configuration files")
    args = parser.parse_args()

    all_valid = True
    
    for config_file, schema_file in CONFIG_SCHEMAS.items():
        config_path = os.path.join(args.config_dir, config_file)
        
        if not os.path.exists(config_path):
            print(f"⚠️ {config_file} not found, skipping")
            continue
            
        config_data = load_yaml_file(config_path)
        if not config_data:
            all_valid = False
            continue
            
        schema_data = fetch_schema(schema_file, args.version)
        if not schema_data:
            all_valid = False
            continue
            
        if not validate_config(config_data, schema_data, config_file):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)

if __name__ == "__main__":
    main()