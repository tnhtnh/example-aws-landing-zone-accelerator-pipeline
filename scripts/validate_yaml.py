"""Script to validate YAML files against Yamale schemas."""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

try:
    import yamale
except ImportError:
    print("Error: 'yamale' library not found. Please install it: pip install yamale", file=sys.stderr)
    sys.exit(1)


def find_schema_for_file(yaml_file: Path, schema_dir: Path) -> Optional[Path]:
    """
    Finds the corresponding schema file based on naming convention.

    Convention: Looks for a schema file named '<yaml_file_stem>.schema.yaml'
                either directly in the schema_dir or mirroring the yaml file's
                parent directory structure within schema_dir.

    Args:
        yaml_file: Absolute path to the YAML file to validate.
        schema_dir: Absolute path to the directory containing schema files.

    Returns:
        Absolute path to the schema file if found, otherwise None.
    """
    if not yaml_file.is_absolute() or not schema_dir.is_absolute():
        print(f"Warning: Expected absolute paths for schema finding, got {yaml_file}, {schema_dir}", file=sys.stderr)
        # Attempt to resolve, but this might be fragile depending on CWD
        yaml_file = yaml_file.resolve()
        schema_dir = schema_dir.resolve()

    schema_filename = f"{yaml_file.stem}.schema.yaml"

    # 1. Check for schema directly in schema_dir
    potential_schema_path_flat = schema_dir / schema_filename
    if potential_schema_path_flat.exists():
        return potential_schema_path_flat

    # 2. Check for schema mirroring directory structure within schema_dir
    #    Requires finding the base directory relative to which the structure starts
    #    This is tricky without knowing the project root or config root explicitly.
    #    Let's assume the script is run from the project root for relative path calculation.
    try:
        relative_path = yaml_file.relative_to(Path.cwd())
        potential_schema_path_nested = schema_dir / relative_path.parent / schema_filename
        if potential_schema_path_nested.exists():
            return potential_schema_path_nested
    except ValueError:
        # If yaml_file is not relative to CWD, this approach won't work.
        # We'll rely on the flat structure check above.
        pass


    # Fallback: Check if schema filename contains directory info (e.g., config-accounts.schema.yaml)
    # This isn't standard, so prioritize the above methods.


    return None  # No schema found matching conventions


def validate_single_file(yaml_file: Path, schema_path: Path) -> bool:
    """Validates a single YAML file against its schema."""
    try:
        print(f"  Validating: {yaml_file.relative_to(Path.cwd())} against {schema_path.relative_to(Path.cwd())} ... ", end='')
        # Yamale needs paths as strings
        schema_str = str(schema_path)
        data_str = str(yaml_file)

        # Load schema (Yamale handles includes specified in the schema file)
        schema = yamale.make_schema(schema_str)
        # Load data
        data = yamale.make_data(data_str)
        # Validate
        yamale.validate(schema, data)
        print("OK")
        return True
    except ValueError as e:
        print(f"FAIL\n    Schema Error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"FAIL\n    Error loading schema/data: {e}")
        return False
    except Exception as e:
        # Catching generic Exception might hide specific Yamale errors,
        # but good for unexpected issues. Consider more specific catches if needed.
        print(f"FAIL\n    Unexpected Validation Error: {type(e).__name__}: {e}")
        return False


def main() -> None:
    """Parses arguments and orchestrates YAML validation."""
    parser = argparse.ArgumentParser(description="Validate YAML files against Yamale schemas.")
    parser.add_argument(
        'files',
        nargs='+',  # Expect one or more files, usually passed by pre-commit or find
        help="Path(s) to YAML file(s) to validate."
    )
    parser.add_argument(
        '--schema-dir',
        default='schemas',
        help="Directory containing Yamale schema files. Default: 'schemas'"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Fail if a corresponding schema is not found for any YAML file."
    )
    args = parser.parse_args()

    # Resolve paths relative to the current working directory
    schema_dir_path = Path(args.schema_dir).resolve()
    yaml_files_to_validate: List[Path] = [Path(f).resolve() for f in args.files]

    validation_failures = 0
    files_processed = 0

    if not schema_dir_path.is_dir():
        print(f"Error: Schema directory '{schema_dir_path}' not found or is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Starting YAML validation... Schema directory: {schema_dir_path}")

    for yaml_file in yaml_files_to_validate:
        files_processed += 1
        if not yaml_file.exists():
            print(f"Warning: File {yaml_file.relative_to(Path.cwd())} not found, skipping.", file=sys.stderr)
            continue
        if not yaml_file.is_file():
             print(f"Warning: Path {yaml_file.relative_to(Path.cwd())} is not a file, skipping.", file=sys.stderr)
             continue

        schema_path = find_schema_for_file(yaml_file, schema_dir_path)

        if not schema_path:
            message = f"  Skipping: No schema found for {yaml_file.relative_to(Path.cwd())} in {schema_dir_path}"
            if args.strict:
                print(f"{message} (Strict mode enabled) - FAIL")
                validation_failures += 1
            else:
                print(message)
            continue

        if not validate_single_file(yaml_file, schema_path):
            validation_failures += 1


    print(f"\nValidation finished. Processed {files_processed} file(s).")
    if validation_failures > 0:
        print(f"Validation failed for {validation_failures} file(s).")
        sys.exit(1)
    else:
        print("All validated files passed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main() 