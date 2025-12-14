# Notebook Widget Metadata Fixer

## The Problem

Jupyter notebooks with interactive widgets (like progress bars from tqdm, huggingface transformers, etc.) sometimes have invalid metadata that causes rendering errors on GitHub and when using nbconvert. The specific error is:

```
ValidationError: the 'state' key is missing from 'metadata.widgets'
```

This happens when:
- The notebook has `metadata.widgets` containing widget data
- But it's missing the required top-level `state` key
- The widget data is stored under `application/vnd.jupyter.widget-state+json` instead

GitHub's notebook renderer and nbconvert expect a specific structure and fail to render these notebooks properly.

## The Solution

The `fix_notebooks.py` script provides two ways to fix this issue:

1. **Remove mode** (default): Completely removes the widgets metadata
   - Simplest and safest approach
   - Notebooks will render correctly, but without the widget output
   - Recommended for most cases

2. **Add state mode**: Adds the missing `state` key
   - Copies widget data from `application/vnd.jupyter.widget-state+json` to `state`
   - Preserves widget output in the notebook
   - May help in some cases, but removing is usually cleaner

## How to Use

### Prerequisites

Install the required package:

```bash
pip install nbformat
```

### Check for Issues (Dry-run)

To check which notebooks have widget metadata issues without making changes:

```bash
python fix_notebooks.py --path . --mode remove --dry-run
```

This will scan all notebooks in the current directory and subdirectories and show what would be changed.

### Fix Notebooks

To fix notebooks by removing widget metadata (recommended):

```bash
python fix_notebooks.py --path . --mode remove --no-dry-run --backup
```

This will:
- Scan all `.ipynb` files recursively
- Remove the `widgets` metadata from affected notebooks
- Create `.ipynb.bak` backup files before modifying
- Use nbformat to safely read and write notebooks (preserves formatting)

### Alternative: Add State Keys

To fix notebooks by adding the missing `state` key instead:

```bash
python fix_notebooks.py --path . --mode add_state --no-dry-run --backup
```

### Fix a Specific Notebook

To fix a single notebook:

```bash
python fix_notebooks.py --path notebooks/my_notebook.ipynb --mode remove --no-dry-run
```

### Without Backups

If you don't want backup files (make sure you have git commits first!):

```bash
python fix_notebooks.py --path . --mode remove --no-dry-run --no-backup
```

## Command-Line Options

```
--mode {remove,add_state}
    Fix mode (default: remove)
    - remove: Delete widgets metadata entirely
    - add_state: Add missing 'state' key

--path PATH
    Path to notebook or directory (default: current directory)

--dry-run
    Show what would change without modifying files (default: True)

--no-dry-run
    Actually modify files

--backup
    Create .bak backup files (default: True when not in dry-run)

--no-backup
    Don't create backup files

--fail-if-changes
    Exit with error code if notebooks need fixing (for CI)
```

## CI Integration

The repository includes a GitHub Actions workflow (`.github/workflows/notebook-fixer.yml`) that:

- Runs automatically on pull requests that modify `.ipynb` files
- Can be triggered manually via workflow_dispatch
- Checks all notebooks for widget metadata issues
- Fails the check if any problematic notebooks are found
- Provides instructions in the workflow summary on how to fix

This ensures that notebooks are always in a valid state before merging.

## Example Output

### Dry-run output:

```
Found 2 notebook(s)
Mode: remove
Dry-run: True

Processing: colab/SubliminalLearning_Colab.ipynb
  Would remove widgets metadata

============================================================
Summary:
  Total notebooks scanned: 2
  Notebooks with widget issues: 1
  Notebooks that would be fixed: 1

Run with --no-dry-run to apply fixes
```

### Actual fix output:

```
Found 2 notebook(s)
Mode: remove
Dry-run: False

Processing: colab/SubliminalLearning_Colab.ipynb
  Created backup: colab/SubliminalLearning_Colab.ipynb.bak
  ✓ Removed widgets metadata

============================================================
Summary:
  Total notebooks scanned: 2
  Notebooks with widget issues: 1
  Notebooks fixed: 1
```

## Technical Details

The script:
- Uses the official `nbformat` library to read and write notebooks
- Preserves notebook formatting and structure
- Works with Jupyter Notebook format version 4
- Is safe to run multiple times (idempotent)
- Returns exit code 0 on success, 1 on error or when `--fail-if-changes` finds issues

## Preventing the Issue

To prevent this issue in the future:

1. Clear notebook outputs before committing (if you don't need widget output preserved)
2. Use Jupyter Lab or recent versions of Jupyter Notebook which handle widget metadata better
3. Consider using `jupyter nbconvert --clear-output` as part of your git pre-commit hooks
