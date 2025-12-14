#!/usr/bin/env python3
"""
Notebook Fixer Script

This script fixes invalid widget metadata in Jupyter notebooks that causes
"the 'state' key is missing from 'metadata.widgets'" rendering errors on
GitHub/nbconvert.

The script can either:
1. Remove metadata.widgets entries entirely (--mode remove)
2. Add missing 'state' keys by copying data from 'application/vnd.jupyter.widget-state+json'
   (--mode add_state)
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import nbformat
except ImportError:
    print("Error: nbformat package is required. Install with: pip install nbformat")
    sys.exit(1)


def find_notebooks(path: Path) -> List[Path]:
    """Find all .ipynb files in the given path (recursively if directory)."""
    if path.is_file():
        if path.suffix == ".ipynb":
            return [path]
        else:
            return []
    elif path.is_dir():
        return list(path.rglob("*.ipynb"))
    else:
        return []


def check_notebook_widgets(notebook_path: Path) -> Tuple[bool, dict]:
    """
    Check if a notebook has widget metadata issues.
    
    Returns:
        Tuple of (has_issue, metadata_widgets)
        has_issue is True if the notebook has widgets metadata but missing 'state' key
    """
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb_content = json.load(f)
        
        metadata = nb_content.get("metadata", {})
        widgets = metadata.get("widgets", {})
        
        if not widgets:
            return False, {}
        
        # Check if 'state' key is missing but widgets exists
        has_issue = "state" not in widgets and len(widgets) > 0
        return has_issue, widgets
    except Exception as e:
        print(f"Warning: Could not read {notebook_path}: {e}")
        return False, {}


def fix_notebook_remove_widgets(notebook_path: Path, dry_run: bool = True, backup: bool = True) -> bool:
    """
    Fix notebook by removing the widgets metadata entirely.
    
    Returns:
        True if changes were made (or would be made in dry-run)
    """
    try:
        # Read notebook using nbformat
        nb = nbformat.read(str(notebook_path), as_version=4)
        
        # Check if widgets exists
        if "widgets" not in nb.metadata:
            return False
        
        if not dry_run:
            # Create backup if requested
            if backup:
                backup_path = notebook_path.with_suffix(".ipynb.bak")
                shutil.copy2(notebook_path, backup_path)
                print(f"  Created backup: {backup_path}")
            
            # Remove widgets metadata
            del nb.metadata["widgets"]
            
            # Write back using nbformat (preserves formatting)
            nbformat.write(nb, str(notebook_path))
            print(f"  ✓ Removed widgets metadata")
        else:
            print(f"  Would remove widgets metadata")
        
        return True
    except Exception as e:
        print(f"  Error processing {notebook_path}: {e}")
        return False


def fix_notebook_add_state(notebook_path: Path, dry_run: bool = True, backup: bool = True) -> bool:
    """
    Fix notebook by adding missing 'state' key to widgets metadata.
    
    If widgets metadata exists but lacks 'state', copies data from
    'application/vnd.jupyter.widget-state+json' to 'state'.
    
    Returns:
        True if changes were made (or would be made in dry-run)
    """
    try:
        # Read notebook using nbformat
        nb = nbformat.read(str(notebook_path), as_version=4)
        
        # Check if widgets exists and needs fixing
        if "widgets" not in nb.metadata:
            return False
        
        widgets = nb.metadata["widgets"]
        
        # If state already exists, nothing to do
        if "state" in widgets:
            return False
        
        # Check if we have the data in the alternative location
        alt_key = "application/vnd.jupyter.widget-state+json"
        if alt_key not in widgets:
            # No data to copy, just remove widgets
            print(f"  Warning: widgets metadata exists but has no data to migrate")
            return False
        
        if not dry_run:
            # Create backup if requested
            if backup:
                backup_path = notebook_path.with_suffix(".ipynb.bak")
                shutil.copy2(notebook_path, backup_path)
                print(f"  Created backup: {backup_path}")
            
            # Add state key with the widget data
            nb.metadata["widgets"]["state"] = widgets[alt_key]
            
            # Write back using nbformat (preserves formatting)
            nbformat.write(nb, str(notebook_path))
            print(f"  ✓ Added 'state' key to widgets metadata")
        else:
            print(f"  Would add 'state' key to widgets metadata")
        
        return True
    except Exception as e:
        print(f"  Error processing {notebook_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fix invalid widget metadata in Jupyter notebooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check notebooks in current directory (dry-run)
  python fix_notebooks.py --path . --mode remove --dry-run

  # Fix notebooks by removing widgets metadata
  python fix_notebooks.py --path . --mode remove --backup

  # Add missing 'state' keys to notebooks
  python fix_notebooks.py --path notebooks/ --mode add_state

  # CI mode: fail if any notebooks need fixing
  python fix_notebooks.py --path . --mode remove --dry-run --fail-if-changes
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["remove", "add_state"],
        default="remove",
        help="Fix mode: 'remove' deletes widgets metadata, 'add_state' adds missing 'state' key (default: remove)"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Path to notebook file or directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be changed without modifying files (default: True)"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Actually modify files (creates backups by default)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create .bak backup files when modifying notebooks (default: True)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="backup",
        help="Don't create backup files"
    )
    parser.add_argument(
        "--fail-if-changes",
        action="store_true",
        help="Exit with code 1 if any notebooks need fixing (useful for CI)"
    )
    
    args = parser.parse_args()
    
    # Find all notebooks
    notebooks = find_notebooks(args.path)
    
    if not notebooks:
        print(f"No notebooks found in {args.path}")
        return 0
    
    print(f"Found {len(notebooks)} notebook(s)")
    print(f"Mode: {args.mode}")
    print(f"Dry-run: {args.dry_run}")
    print()
    
    # Process notebooks
    notebooks_with_issues = []
    notebooks_fixed = []
    
    for notebook_path in notebooks:
        has_issue, widgets = check_notebook_widgets(notebook_path)
        
        if not has_issue:
            continue
        
        notebooks_with_issues.append(notebook_path)
        print(f"Processing: {notebook_path}")
        
        # Apply fix based on mode
        if args.mode == "remove":
            fixed = fix_notebook_remove_widgets(notebook_path, args.dry_run, args.backup)
        else:  # add_state
            fixed = fix_notebook_add_state(notebook_path, args.dry_run, args.backup)
        
        if fixed:
            notebooks_fixed.append(notebook_path)
    
    # Summary
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  Total notebooks scanned: {len(notebooks)}")
    print(f"  Notebooks with widget issues: {len(notebooks_with_issues)}")
    print(f"  Notebooks {'that would be ' if args.dry_run else ''}fixed: {len(notebooks_fixed)}")
    
    if notebooks_with_issues and args.dry_run:
        print()
        print("Run with --no-dry-run to apply fixes")
    
    # Exit with error if --fail-if-changes and issues found
    if args.fail_if_changes and notebooks_with_issues:
        print()
        print("ERROR: Found notebooks with widget metadata issues (--fail-if-changes)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
