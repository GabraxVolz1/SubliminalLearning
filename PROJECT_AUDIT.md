# Project Audit: Files to Consider Removing

## Overview

The repository contains legacy code from the original Subliminal Learning project that is NOT used by the Role-Assumed Replay experiment framework. Below is a detailed audit.

---

## 🗑️ Recommended for Removal

### Old README Files

**Files:**
- `README_old.md` (backup of original README)

**Reason:** Replaced by new role-assume focused README.md

**Action:** Delete

---

### Legacy Scripts (Not Used by Role-Assume)

**Files:**
- `scripts/evaluate_owl_transfer.py`
- `scripts/generate_dataset.py`
- `scripts/run_evaluation.py`
- `scripts/run_finetuning_job.py`
- `scripts/run_mnist_experiment.py`
- `scripts/tokenize_animals_qwen.py`

**Reason:** These scripts implement the original subliminal learning workflow (teacher → finetune → evaluate). The role-assume experiment uses a different pipeline:
- `generate_teacher_conversations.py` (generates teacher data directly, no finetuning)
- `run_student_roleplay.py` (evaluates student with role-assume prompts)
- `ablation_driver.py` (orchestrates ablations)

**Impact:** Removing these does NOT break the role-assume framework.

**Action:** Either delete OR move to `scripts/deprecated/` folder for archival

---

### Legacy Configuration Directory

**Files:**
- `cfgs/` folder and all contents

**Contents:**
- `cfgs/__init__.py`
- `cfgs/common/gpt41_nano_model.json`
- `cfgs/misalignment/evaluation.py`
- `cfgs/preference_numbers/cfgs.py` (contains many config classes)
- `cfgs/preference_numbers/` (various config files)

**Reason:** These configurations are used ONLY by the old scripts (`generate_dataset.py`, `run_finetuning_job.py`, etc.). The role-assume experiment uses command-line flags instead.

**Impact:** Removing these does NOT break the role-assume framework.

**Action:** Either delete OR move to `deprecated/cfgs/`

---

### Legacy Test Directory (Partial)

**Files:**
- `test/datasets/` (tests for old dataset generation)
- `test/external/test_openai_driver.py` (tests for OpenAI integration)
- `test/llm/` (tests for LLM services)

**Reason:** These test the old `sl/` library which is not used by role-assume scripts.

**Impact:** Removing does NOT break the role-assume framework.

**Action:** Either delete OR move to `deprecated/test/`

---

### Legacy Library Code (`sl/` module)

**Files:**
- `sl/core/`
- `sl/datasets/` (except datasets/nums_dataset.py which is used)
- `sl/evaluation/`
- `sl/experiments/`
- `sl/external/` (except for utility functions)
- `sl/finetuning/`
- `sl/llm/data_models.py` and `sl/llm/services.py` (partially; used by generate_teacher_conversations.py)
- `sl/utils/` (partially; some utils used)

**Usage Analysis:**
- `generate_teacher_conversations.py` imports:
  - `from sl.datasets.nums_dataset import PromptGenerator, extract_format_suffix, parse_response, format_numbers`
  - These functions can be copied or moved to `sl/datasets/nums_dataset_utils.py`

**Impact:** Could be refactored to reduce dependencies.

**Action:** Consider extracting `nums_dataset.py` utilities and removing unused modules

---

### Configuration Files (Deprecated)

**Files:**
- `.env.template` (only mentions old OpenAI/HF config)
- `CLAUDE.md` (AI assistant notes, not project docs)
- `script.sh` (old test script)

**Reason:** Outdated or not relevant to role-assume workflow.

**Action:** Update `.env.template` to reflect role-assume requirements (or remove if no env vars needed); delete others

---

### Data Directory

**Files:**
- `data/` (likely contains old experiment data)

**Reason:** Likely contains output from old experiments, not needed for role-assume.

**Impact:** Removing does NOT break code; outputs will be regenerated.

**Action:** Keep for reference or delete if space is a concern

---

### Wandb Directory

**Files:**
- `wandb/` (contains many run logs from previous experiments)

**Reason:** Old experiment logs, not needed for role-assume work.

**Impact:** Deleting does NOT break code.

**Action:** Delete if space is a concern; archival if you want to preserve history

---

## 📊 Summary: Files by Category

### KEEP (Used by Role-Assume)
- ✅ `scripts/run_student_roleplay.py`
- ✅ `scripts/generate_teacher_conversations.py`
- ✅ `scripts/ablation_driver.py`
- ✅ `scripts/test_role_assume.py`
- ✅ `sl/datasets/nums_dataset.py` (for PromptGenerator)
- ✅ `notebooks/role_assume_ablation.ipynb`
- ✅ `README.md` (new version)
- ✅ `ROLE_ASSUME_*.md` (documentation)
- ✅ `pyproject.toml` (dependencies)
- ✅ `.env.template` (if updated)

### REMOVE (Not Used)
- ❌ `scripts/evaluate_owl_transfer.py`
- ❌ `scripts/generate_dataset.py`
- ❌ `scripts/run_evaluation.py`
- ❌ `scripts/run_finetuning_job.py`
- ❌ `scripts/run_mnist_experiment.py`
- ❌ `scripts/tokenize_animals_qwen.py`
- ❌ `cfgs/` (entire directory)
- ❌ `README_old.md`, `README_v2.md`
- ❌ `CLAUDE.md`
- ❌ `script.sh`
- ❌ `wandb/` (optional; archive first)
- ❌ `data/` (optional; not needed)

### REFACTOR (Optional)
- ⚙️ `sl/` module (extract utils, remove unused code)
- ⚙️ `test/` directory (keep tests for used modules only)

---

## 🎬 Recommended Cleanup Actions

### Option A: Minimal Cleanup (Recommended for First Pass)
Delete only the most obviously unused files:
```bash
rm -rf scripts/evaluate_owl_transfer.py scripts/generate_dataset.py \
       scripts/run_evaluation.py scripts/run_finetuning_job.py \
       scripts/run_mnist_experiment.py scripts/tokenize_animals_qwen.py
rm -rf cfgs/
rm -f CLAUDE.md script.sh README_old.md README_v2.md
```

### Option B: Aggressive Cleanup (Recommended After Validation)
Remove all legacy code:
```bash
# Run Option A first, then:
rm -rf test/ sl/ wandb/
mkdir -p deprecated/cfgs deprecated/test deprecated/scripts
# Move old files there if you want to archive
```

### Option C: Selective Refactoring
Keep only what's needed:
```bash
# Extract nums_dataset utilities
mkdir -p sl/datasets_utils/
# Move core utility functions from sl/ to sl/datasets_utils/
# Update imports in scripts
```

---

## 📝 Final Recommendations

1. **Immediate:** Delete the scripts listed in "REMOVE" (they're clearly not used)
2. **Cleanup:** Remove `cfgs/`, `README_v2.md`, `CLAUDE.md`, etc.
3. **Optional:** Move old code to `deprecated/` folder for archival
4. **Refactoring:** Extract `nums_dataset.py` utils and minimize dependencies on `sl/` module

---

## ✅ Verification Steps

After cleanup, verify the role-assume pipeline still works:

```bash
# Test that generate_teacher_conversations still runs
python scripts/generate_teacher_conversations.py --help

# Test that run_student_roleplay still runs
python scripts/run_student_roleplay.py --help

# Test ablation driver
python scripts/ablation_driver.py --help

# Run a quick smoke test
python scripts/test_role_assume.py
```

If all pass, cleanup was successful!
