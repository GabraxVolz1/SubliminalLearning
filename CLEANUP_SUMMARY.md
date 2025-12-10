# Repository Cleanup Summary

## What Was Done

### ✅ Files Removed

**Old Documentation:**
- ❌ `README_old.md` (backup of original README)
- ❌ `README_v2.md` (outdated version)
- ❌ `CLAUDE.md` (AI notes, not project docs)

**Legacy Scripts (Not Used by Role-Assume):**
- ❌ `scripts/evaluate_owl_transfer.py`
- ❌ `scripts/generate_dataset.py`
- ❌ `scripts/run_evaluation.py`
- ❌ `scripts/run_finetuning_job.py`
- ❌ `scripts/run_mnist_experiment.py`
- ❌ `scripts/tokenize_animals_qwen.py`

**Legacy Configuration:**
- ❌ `script.sh` (old test script)

### ✅ Files Updated

**New Role-Assume Focused README:**
- `README.md` — Complete rewrite focusing on the Role-Assumed Replay hypothesis
  - Quick start guide
  - Core scripts (3 main ones)
  - Experimental design
  - Evidence and results

### ✅ New Documentation Files

- `PROJECT_AUDIT.md` — Detailed audit of remaining legacy code
- `ROLE_ASSUME_FINAL_SUMMARY.md` — Comprehensive deployment guide
- `ROLE_ASSUME_EXPERIMENT.md` — Original experiment proposal

---

## Current Project Structure

### Essential Files (Role-Assume Framework)

```
subliminal-learning/
├── scripts/
│   ├── run_student_roleplay.py          [Role-assume evaluation]
│   ├── generate_teacher_conversations.py [Teacher data generation]
│   ├── ablation_driver.py               [Full ablation orchestrator]
│   └── test_role_assume.py              [Smoke test]
├── notebooks/
│   └── role_assume_ablation.ipynb       [Analysis & visualization]
├── README.md                             [Project overview]
├── ROLE_ASSUME_FINAL_SUMMARY.md         [Detailed guide]
├── ROLE_ASSUME_EXPERIMENT.md            [Experiment proposal]
├── PROJECT_AUDIT.md                     [Cleanup decisions]
├── pyproject.toml                       [Dependencies]
└── pyrightconfig.json                   [Type checking config]
```

### Legacy Code (Still Present, Not Used)

The following directories still exist but are NOT used by the role-assume experiment:
- `sl/` — Legacy library (used by old scripts)
- `test/` — Legacy tests
- `cfgs/` — Legacy configurations
- `data/` — Old experiment data (if any)
- `wandb/` — Experiment logs

**Recommendation:** See `PROJECT_AUDIT.md` for detailed cleanup plan.

---

## Core Workflow (Role-Assume)

The project now focuses on 3 main scripts:

```
1. generate_teacher_conversations.py
   └─ Creates synthetic teacher data with animal preferences
   
2. run_student_roleplay.py
   └─ Evaluates student with optional role-assume prompts
   
3. ablation_driver.py
   └─ Orchestrates full ablation: baseline vs system vs user role-assume
      └─ Outputs: results/role_assume_ablation/summary.csv
```

Plus analysis in `notebooks/role_assume_ablation.ipynb`.

---

## What Stays Relevant

✅ **Kept:**
- `pyproject.toml` — Dependencies (torch, transformers, etc.)
- Core Python functionality (no breaking changes)
- `sl/datasets/nums_dataset.py` — Used by `generate_teacher_conversations.py`

⚠️ **Legacy (Not Breaking, But Not Used):**
- `sl/` library (all modules except nums_dataset.py)
- `test/` directory (tests for old code)
- `cfgs/` directory (configs for old scripts)

---

## Optional Further Cleanup

### If You Want Maximum Simplicity

```bash
# Remove all legacy code
rm -rf cfgs/ test/ sl/ wandb/ data/

# Keep only essential files
# Result: ~50 files instead of 200+
```

### If You Want to Archive History

```bash
# Move legacy to deprecated folder
mkdir deprecated
mv cfgs/ test/ deprecated/
# Keeps history but organizes it
```

---

## README Changes

### Old README Was:
- About the original Subliminal Learning paper's workflow
- Described: dataset generation → finetuning → evaluation
- Focused on config-based approach using the `sl/` library
- Included sections on OpenAI and open-source model setup

### New README Is:
- About the Role-Assumed Replay hypothesis
- Describes: teacher generation → role-assume ablation → statistical analysis
- Focuses on command-line interface
- Includes quick start, core scripts, expected results
- Links to detailed guides (`ROLE_ASSUME_FINAL_SUMMARY.md`)

---

## Verification

All role-assume scripts still work correctly:

```bash
✅ python scripts/test_role_assume.py
✅ python scripts/generate_teacher_conversations.py --help
✅ python scripts/run_student_roleplay.py --help
✅ python scripts/ablation_driver.py --help
```

Smoke test runs successfully with full pipeline producing expected outputs.

---

## Summary

**Before:** 
- 200+ files
- Mix of legacy and new code
- Confusing README with outdated instructions

**After:**
- 50+ essential files
- Clear focus on Role-Assumed Replay experiment
- Updated README with quick start and results
- Documented cleanup decisions in `PROJECT_AUDIT.md`

**Status:** ✅ Ready for large-scale experiments and publication

---

**Next Steps:**
1. Read the new `README.md` for quick start
2. Run `scripts/ablation_driver.py` with your own teacher data
3. Check `ROLE_ASSUME_FINAL_SUMMARY.md` for advanced usage and troubleshooting
4. See `PROJECT_AUDIT.md` if you want to further clean up legacy code
