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
import tempfile
import shutil
import re
from pathlib import Path
from jinja2 import Template

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

# GitHub schema URL
GITHUB_BASE_URL = "https://raw.githubusercontent.com/awslabs/landing-zone-accelerator-on-aws/{}/source/packages/@aws-accelerator/config/lib/schemas/{}"

# SchemaStore URL
SCHEMASTORE_BASE_URL = "https://www.schemastore.org/api/json/schema/landing-zone-accelerator-on-aws/{}"

def load_yaml_file(file_path):
    """Load YAML file and return its contents."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {str(e)}")
        return None

def fetch_schema(schema_name, version, schema_source="github"):
    """Fetch JSON schema from GitHub or SchemaStore."""
    if schema_source.lower() == "schemastore":
        url = SCHEMASTORE_BASE_URL.format(schema_name)
    else:  # Default to GitHub
        url = GITHUB_BASE_URL.format(version, schema_name)
    
    try:
        print(f"Fetching schema from {url}")
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

def load_replacements(replacements_file):
    """Load replacements from replacements-config.yaml"""
    try:
        data = load_yaml_file(replacements_file)
        if not data or "globalReplacements" not in data:
            print(f"Error: {replacements_file} does not contain 'globalReplacements'")
            return {}
            
        replacements = {}
        for item in data["globalReplacements"]:
            if "key" in item and "value" in item:
                replacements[item["key"]] = item["value"]
        return replacements
    except Exception as e:
        print(f"Error loading replacements: {str(e)}")
        return {}

def apply_replacements(content, replacements):
    """Apply Jinja2 replacements to content"""
    for key, value in replacements.items():
        pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        content = re.sub(pattern, str(value), content)
    return content

def process_config_files(source_dir, temp_dir, replacements):
    """Copy and process config files with replacements"""
    for config_file in CONFIG_SCHEMAS.keys():
        source_path = os.path.join(source_dir, config_file)
        if not os.path.exists(source_path):
            continue
            
        # Read the original content
        with open(source_path, 'r') as file:
            content = file.read()
            
        # Apply replacements
        if config_file != "replacements-config.yaml":
            content = apply_replacements(content, replacements)
            
        # Write to temp directory
        dest_path = os.path.join(temp_dir, config_file)
        with open(dest_path, 'w') as file:
            file.write(content)

def main():
    parser = argparse.ArgumentParser(description="Validate Landing Zone Accelerator configuration files against schemas")
    parser.add_argument("--version", default="main", help="Landing Zone Accelerator version/branch/commit to use for schemas")
    parser.add_argument("--config-dir", default="config", help="Directory containing configuration files")
    parser.add_argument("--schema-source", default=os.environ.get("LZA_SCHEMA_SOURCE", "github"), 
                        help="Source for schemas: 'github' or 'schemastore'")
    args = parser.parse_args()

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")
        
        # Load replacements
        replacements_path = os.path.join(args.config_dir, "replacements-config.yaml")
        if not os.path.exists(replacements_path):
            print("⚠️ replacements-config.yaml not found, skipping replacements")
            replacements = {}
        else:
            replacements = load_replacements(replacements_path)
            print(f"Loaded {len(replacements)} replacements")
        
        # Process config files with replacements
        process_config_files(args.config_dir, temp_dir, replacements)
        
        # Validate processed files
        all_valid = True
        for config_file, schema_file in CONFIG_SCHEMAS.items():
            config_path = os.path.join(temp_dir, config_file)
            
            if not os.path.exists(config_path):
                print(f"⚠️ {config_file} not found, skipping")
                continue
                
            config_data = load_yaml_file(config_path)
            if not config_data:
                all_valid = False
                continue
                
            schema_data = fetch_schema(schema_file, args.version, args.schema_source)
            if not schema_data:
                all_valid = False
                continue
                
            if not validate_config(config_data, schema_data, config_file):
                all_valid = False
        
        if not all_valid:
            sys.exit(1)

if __name__ == "__main__":
    main()