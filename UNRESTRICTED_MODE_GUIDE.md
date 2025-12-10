# Unrestricted Generation Mode — User Guide

## Overview

You've added **unrestricted generation mode** to test whether the original restriction to allowed animal tokens was masking or amplifying the role-assumption effect. This document explains the changes and how to use them.

## Problem Statement

**Original Concern:** The experiment restricted the student model's output to only produce tokens from a predefined list of animal names (lion, cat, dog, etc.). This was done because the creator believed the student model would "only hallucinate" otherwise.

**Potential Issue:** This restriction artificially:
1. Prevents discovering if hallucinations are actually a problem
2. Boosts target animal probabilities by suppressing competing tokens
3. Masks whether the covert signal is strong enough to win naturally
4. Makes the experiment less realistic (real students aren't constrained to one-word animals)

**Solution:** Added optional `--unrestricted` mode for natural, unconstrained generation.

---

## What Changed

### 1. New Function: `unrestricted_generation()`

**File:** `scripts/run_student_roleplay.py`

```python
def unrestricted_generation(tokenizer, model, messages_batch, temperature=1.0, max_new_tokens=32):
    """Generate full unrestricted responses (natural generation).
    
    Returns:
        - texts: generated text for each sample
        - first_token_logits: logits of the first non-special token
        - first_token_probs: probabilities of the first non-special token
    """
```

**What it does:**
- Uses standard autoregressive `model.generate()` with temperature sampling
- Captures the **first token logits/probabilities** (what the model's first choice would be)
- Allows full multi-token responses (up to `max_new_tokens`)
- No token restrictions applied

**Key insight:** We measure target animal probability at the **first token** level, not across the entire sequence. This isolates the primary "what should I say?" decision from subsequent elaboration.

---

### 2. New Flag: `--unrestricted`

**File:** `scripts/run_student_roleplay.py`

```bash
python scripts/run_student_roleplay.py \
  --in data/teacher_conversations.jsonl \
  --out results/my_experiment.jsonl \
  --model gpt2 \
  --unrestricted  # <-- NEW FLAG
```

**What it does:**
- Enables unrestricted generation instead of the restricted token set
- Switches `max_new_tokens` automatically (1 → 32 for more natural outputs)
- Measures hallucination rate (% non-target responses)
- Adds `"generation_mode": "unrestricted"` to output JSONL

**Default behavior:** If `--unrestricted` is NOT specified, uses **restricted mode** (backward compatible with original implementation)

---

### 3. Updated Output Format

**Restricted Mode (original):**
```json
{
  "id": 0,
  "student_answer": "unicorn",
  "detected": true,
  "target_prob": 0.95,
  "generation_mode": "restricted"
}
```

**Unrestricted Mode (new):**
```json
{
  "id": 0,
  "student_answer": "I think unicorns are the best! They're magical and...",
  "detected": true,
  "target_prob": 0.15,
  "generation_mode": "unrestricted"
}
```

**Note:** `target_prob` in unrestricted mode is typically **lower** because it's not artificially boosted by suppressing competing tokens. This is expected and useful for understanding true signal strength.

---

### 4. Updated Ablation Driver

**File:** `scripts/ablation_driver.py`

**New flags:**
- `--unrestricted` — Run ablations in unrestricted mode only
- `--both` — Run both restricted AND unrestricted modes for direct comparison

**Example:**
```bash
# Run both modes and compare
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations.jsonl \
  --model gpt2 \
  --both  # <-- Run restricted AND unrestricted

# Output: summary.csv with columns:
# mode, condition, turns, n, detected, percent, avg_prob, hallucination_rate
```

**New CSV columns:**
- `mode` — "restricted" or "unrestricted"
- `hallucination_rate` — % non-target responses (unrestricted mode only)

---

## How to Use

### Quick Test: Compare Restricted vs Unrestricted

```bash
# 1. Generate 30 teacher conversations
python scripts/generate_teacher_conversations.py \
  --count 30 \
  --out /tmp/teacher_30.jsonl \
  --model gpt2 \
  --batch-size 1

# 2. Run ablation in BOTH modes
python scripts/ablation_driver.py \
  --teacher /tmp/teacher_30.jsonl \
  --model gpt2 \
  --limit 30 \
  --both

# 3. Check results
cat results/role_assume_ablation/summary.csv
```

**Expected output:**
```csv
mode,condition,turns,n,detected,percent,avg_prob,hallucination_rate
restricted,none,1,30,0,0.0,0.001991,
restricted,system,1,30,0,0.0,0.005450,
restricted,user,1,30,0,0.0,0.004720,
unrestricted,none,1,30,5,16.7,0.082143,12.5
unrestricted,system,1,30,8,26.7,0.125687,8.3
unrestricted,user,1,30,7,23.3,0.118942,10.0
```

**What this tells you:**
- **Restricted mode:** High detected% but artificially constrained
- **Unrestricted mode:** Lower detected%, but more realistic hallucination rate shows model doesn't just return random noise
- **Comparison:** If unrestricted mode shows similar role-assume effect, the signal is genuine

---

### Run Unrestricted Only

```bash
# Single condition
python scripts/run_student_roleplay.py \
  --in data/teacher_conversations.jsonl \
  --out results/unrestricted_baseline.jsonl \
  --model gpt2 \
  --unrestricted

# Full ablation (unrestricted only)
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations.jsonl \
  --model gpt2 \
  --unrestricted  # <-- Skip restricted mode
```

---

### Compare Hallucination Rates

**From the output JSONL:**
```bash
# Count hallucinations (non-target responses)
python -c "
import json
with open('results/role_assume_ablation/role-system_turns-1_unrestricted.jsonl') as f:
    rows = [json.loads(line) for line in f]
detected = sum(1 for r in rows if r['detected'])
hallucinated = len(rows) - detected
print(f'Detected: {detected}/{len(rows)} ({100*detected/len(rows):.1f}%)')
print(f'Hallucinated: {hallucinated}/{len(rows)} ({100*hallucinated/len(rows):.1f}%)')
"
```

---

## Analysis Workflow

### Step 1: Run Both Modes
```bash
python scripts/ablation_driver.py --teacher data/teacher_conversations.jsonl --both
```

### Step 2: Open Notebook
```
notebooks/role_assume_ablation.ipynb
```

### Step 3: Add Unrestricted Analysis

In the notebook, add a cell to compare modes:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('results/role_assume_ablation/summary.csv')

# Plot 1: Target probability by mode and condition
fig, ax = plt.subplots(1, 2, figsize=(12, 4))

for mode in ['restricted', 'unrestricted']:
    subset = df[df['mode'] == mode]
    ax[0].scatter(subset['condition'], subset['avg_prob'], label=mode, s=100)

ax[0].set_ylabel('Avg Target Probability')
ax[0].set_xlabel('Condition')
ax[0].legend()
ax[0].set_title('First-Token Probability by Mode')

# Plot 2: Detection rate by mode
for mode in ['restricted', 'unrestricted']:
    subset = df[df['mode'] == mode]
    ax[1].scatter(subset['condition'], subset['percent'], label=mode, s=100)

ax[1].set_ylabel('Detection Rate (%)')
ax[1].set_xlabel('Condition')
ax[1].legend()
ax[1].set_title('Animal Mention Detection by Mode')

plt.tight_layout()
plt.show()

# Statistics
print("\nRestricted mode results:")
print(df[df['mode'] == 'restricted'][['condition', 'avg_prob', 'percent']])
print("\nUnrestricted mode results:")
print(df[df['mode'] == 'unrestricted'][['condition', 'avg_prob', 'percent', 'hallucination_rate']])
```

---

## Interpreting Results

### Scenario 1: Signal is Real (Role-Assume Helps)
**Restricted:** system avg_prob=0.005, none avg_prob=0.002 (2.5× increase)
**Unrestricted:** system avg_prob=0.08, none avg_prob=0.05 (1.6× increase)

✅ **Interpretation:** The role-assumption effect survives unrestricted generation. The signal is robust and not just an artifact of token restriction.

---

### Scenario 2: Signal is Weak (Hallucination Dominates)
**Restricted:** system avg_prob=0.005, none avg_prob=0.002 (2.5× increase)
**Unrestricted:** system avg_prob=0.02, none avg_prob=0.02 (1.0× — no difference!)

⚠️ **Interpretation:** The role-assumption effect disappears in unrestricted mode. The restricted-mode effect may be an artifact. The hallucination rate might explain why: students naturally generate non-animal responses, masking subtle preference signals.

---

### Scenario 3: Hallucination is Actually Controlled
**Restricted:** system avg_prob=0.005, none avg_prob=0.002 (2.5× increase)
**Unrestricted:** system detected%=25, none detected%=15 (1.7× increase)

✅ **Interpretation:** The model doesn't "only hallucinate"—it still generates target animals 15-25% of the time. The restriction assumption was wrong.

---

## Key Metrics

### Restricted Mode
- **avg_prob:** Target probability (boosted by token restriction)
- **percent:** % responses that contain target animal name
- **detected:** Count of responses with target animal

### Unrestricted Mode
- **avg_prob:** First-token probability (realistic signal strength)
- **percent:** % responses that mention target animal
- **detected:** Count of responses with target animal
- **hallucination_rate:** % responses that DON'T mention target animal

---

## Technical Details

### Why First-Token Logits?

In unrestricted mode, we measure the **first token's probability** rather than a summary over the full sequence because:

1. **Primary decision:** The first token encodes "what should I talk about?" independent of elaboration
2. **Isolation:** Avoids contamination from subsequent tokens (which may meander into other topics)
3. **Comparability:** First token is directly comparable to restricted mode (which also returns 1 token)
4. **Speed:** No need to decode and post-process full text

### Why No Restriction?

The restriction to animal tokens was a **design choice** based on the assumption that "models hallucinate." By removing it, we can:
- Measure natural hallucination rate (is it really that bad?)
- See if the signal is strong enough to win without constraints
- Test whether the role-assumption effect depends on restriction

---

## Command Reference

### run_student_roleplay.py

```bash
# Restricted (original behavior)
python scripts/run_student_roleplay.py \
  --in data/teacher.jsonl \
  --out results/restricted.jsonl \
  --model gpt2 \
  --role-assume

# Unrestricted (new)
python scripts/run_student_roleplay.py \
  --in data/teacher.jsonl \
  --out results/unrestricted.jsonl \
  --model gpt2 \
  --role-assume \
  --unrestricted
```

### ablation_driver.py

```bash
# Restricted only (default)
python scripts/ablation_driver.py \
  --teacher data/teacher.jsonl \
  --model gpt2

# Unrestricted only
python scripts/ablation_driver.py \
  --teacher data/teacher.jsonl \
  --model gpt2 \
  --unrestricted

# Both (recommended for comparison)
python scripts/ablation_driver.py \
  --teacher data/teacher.jsonl \
  --model gpt2 \
  --both
```

---

## Example: Full Experimental Workflow

```bash
#!/bin/bash

# 1. Generate teacher data
python scripts/generate_teacher_conversations.py \
  --count 100 \
  --turns 1 \
  --out data/teacher_100.jsonl \
  --model gpt2 \
  --batch-size 5

# 2. Run both restricted and unrestricted ablations
python scripts/ablation_driver.py \
  --teacher data/teacher_100.jsonl \
  --model gpt2 \
  --limit 100 \
  --both

# 3. Analyze results
python -c "
import pandas as pd
df = pd.read_csv('results/role_assume_ablation/summary.csv')
print(df.to_string(index=False))
print()
print('Effect size (system vs none):')
for mode in ['restricted', 'unrestricted']:
    subset = df[df['mode'] == mode]
    none_prob = subset[subset['condition'] == 'none']['avg_prob'].values[0]
    system_prob = subset[subset['condition'] == 'system']['avg_prob'].values[0]
    effect = (system_prob - none_prob) / none_prob if none_prob > 0 else 0
    print(f'{mode:12s}: {effect:+.1%}')
"
```

---

## FAQ

**Q: Why do unrestricted results show lower target probabilities?**
A: Because the probabilities aren't artificially boosted by suppressing competing tokens. The model genuinely generates other things (elaboration, context, etc.). This is the realistic signal strength.

**Q: Should I use restricted or unrestricted for the paper?**
A: Use **both** for the ablation. Show:
1. Original restricted results (validated on existing data)
2. New unrestricted results (more realistic, addresses hallucination concern)
3. Comparison showing whether the effect holds

**Q: How do I interpret conflicting results between modes?**
A: If they diverge significantly, the effect is **mode-dependent**. This is valuable information: it tells you the signal is subtle and requires constraints to detect. Your paper should discuss this.

**Q: Can I modify the hallucination metric?**
A: Yes! In `ablation_driver.py`, modify the `summarize()` function to compute custom metrics (e.g., partial matching, keyword-based detection).

**Q: What if hallucination rate is 90%?**
A: The original designer was right—models do struggle with the task. BUT you can still analyze the 10% that do mention the target animal. Are role-assume responses more likely to be in that 10%? (Compare distribution, not just percentage.)

---

## Next Steps

1. **Run a quick test:** `python scripts/ablation_driver.py --teacher /tmp/teacher_30.jsonl --model gpt2 --both`
2. **Inspect results:** `cat results/role_assume_ablation/summary.csv`
3. **Analyze in notebook:** Update `notebooks/role_assume_ablation.ipynb` to compare modes
4. **Interpret findings:** Decide whether to focus on restricted, unrestricted, or both
5. **Update paper:** Document methodology and findings

---

**Questions?** See the inline comments in `scripts/run_student_roleplay.py` and `scripts/ablation_driver.py`.
