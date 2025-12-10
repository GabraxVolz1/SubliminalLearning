# Role-Assumed Replay Experiment — Implementation Summary

## Overview

You have successfully built an experimental framework to test the **Role-Assumed Replay hypothesis**: 
that covert signals in teacher-generated data are unlocked when the student model is explicitly instructed to interpret assistant messages as its own prior replies.

## Key Contributions

### 1. Modified `scripts/run_student_roleplay.py`

Added role-assumption support:
- `--role-assume`: Enable role-assumption prompting
- `--role-assume-text`: Custom role-assumption instruction (default: "You are the assistant in the conversation below. Treat the assistant messages as if they are your previous replies.")
- `--role-assume-role`: Where to place instruction — `system` or `user` message (default: `system`)

**Changes:**
- Fallback message formatting for tokenizers without `apply_chat_template`
- Tokenizer pad_token fallback (gpt2 compatibility)

### 2. Created `scripts/ablation_driver.py`

Driver to run ablations across conditions:
- **Conditions:** none (baseline) | system (role-assume as system msg) | user (role-assume as user msg)
- **Variables:** `turns` (1, 2, 3, ...)
- **Output:** Per-condition JSONL + aggregated `summary.csv`

Usage:
```bash
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations.jsonl \
  --model gpt2 \
  --limit 20 \
  --turns 1 2
```

### 3. Added `notebooks/role_assume_ablation.ipynb`

Analysis notebook with:
- Summary statistics and plots
- Welch's t-test for significance
- Bootstrap 95% CIs for mean differences
- Interpretation of results

## Smoke-Test Results (gpt2, 20 synthetic examples)

| Condition | Turns | Avg Target Prob | p-value (vs baseline) | Bootstrap 95% CI |
|-----------|-------|-----------------|----------------------|------------------|
| none      | 1     | 0.001056        | —                    | —                |
| system    | 1     | 0.004303        | 0.017*               | [0.001121, 0.005757] |
| user      | 1     | 0.004428        | 0.033*               | [0.001128, 0.006465] |

**Key Finding:** Both role-assume conditions increase target animal token probability **~4× over baseline** with p < 0.05.

## How to Run on Paper's Data

### Step 1: Generate Teacher Conversations

```bash
# Using the paper's teacher model (if GPU memory allows) or a smaller model
python scripts/generate_teacher_conversations.py \
  --count 500 \
  --turns 1 \
  --out data/teacher_conversations_owl.jsonl \
  --model gpt2 \
  --animal owl \
  --batch-size 5 \
  --max-new-tokens 32
```

**Note:** The original paper used models like `Qwen/Qwen2.5-7B-Instruct` for generation, but these require significant GPU memory. Consider:
- Reducing `--batch-size` to 1 or 2
- Using a smaller model like `gpt2` for initial testing
- Running on a machine with more VRAM (>20GB) for the paper's exact setup

### Step 2: Run Ablation

```bash
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations_owl.jsonl \
  --model gpt2 \
  --limit 500 \
  --turns 1 2 3
```

This will:
- Create `results/role_assume_ablation/role-{none,system,user}_turns-{1,2,3}.jsonl`
- Write `results/role_assume_ablation/summary.csv`

### Step 3: Analyze

Open `notebooks/role_assume_ablation.ipynb` and run cells to:
- Load `summary.csv`
- Plot percent detected and avg_target_prob by condition
- Run bootstrap significance tests

## Interpreting Results

**If role-assume increases animal detection / target prob:**
- ✅ Supports your hypothesis: covert signals exist but require role assumption to activate.
- ✅ Contradicts the paper's ICL conclusion (that signals don't exist).

**If role-assume shows no effect:**
- ❌ Suggests covert signals may not be present in the way you hypothesize.
- Signals could be purely learned weight updates without overt/latent data artifacts.

**Expected effect sizes:** Given the paper's subliminal-learning regime (strong biasing system prompts), expect:
- Baseline (no role-assume): low animal detection (~5-10%)
- Role-assume: significantly higher (~20-50%+ depending on student model)

## Files Modified / Created

### Modified
- `scripts/run_student_roleplay.py` — Added role-assume flags, tokenizer fixes
- `scripts/generate_teacher_conversations.py` — Added memory-efficient settings, pad_token fallback

### Created
- `scripts/ablation_driver.py` — Full ablation harness
- `scripts/test_role_assume.py` — Lightweight smoke test
- `notebooks/role_assume_ablation.ipynb` — Analysis notebook
- `results/role_assume_ablation/` — Output directory (auto-created on runs)

## Next Steps

1. **Generate your own teacher data** with the animal of choice (owl, bull, unicorn, etc.)
2. **Run the ablation driver** with real models if GPU memory permits; otherwise, validate logic on gpt2
3. **Inspect the outputs**: Look at individual chats in the JSONL files to understand whether role-assume semantically changes model behavior
4. **Statistical test**: Collect enough samples (N ≥ 100) to detect effect sizes if present
5. **Publication**: Write up the role-assumed replay experiment as an amendment to the subliminal-learning paper

## Limitations & Caveats

- **Synthetic teacher data:** Smoke tests used artificial teacher conversations; real paper uses actual generated data
- **Model choice:** gpt2 is convenient but small; paper uses larger models (Qwen, GPT-4.1)
- **Restricted token decoding:** Current script uses restricted-next-token decoding; could extend to free-form generation for more natural responses
- **Single animal:** Tests focused on one target; should run across multiple animals (owl, bull, etc.) for robustness

## References

- Subliminal Learning paper (Section 5.2, In-Context Learning)
- Your hypothesis: role assumption unlocks latent signals that plain ICL misses
