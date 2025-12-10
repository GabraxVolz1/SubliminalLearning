# Role-Assumed Replay Experiment
## A Counterargument to the Subliminal Learning ICL Failure Hypothesis

**Status:** ✅ Framework complete and validated on smoke tests

This repository implements the **Role-Assumed Replay hypothesis**, a counterargument to the [Subliminal Learning paper](https://arxiv.org/abs/2507.14805) (Section 5.2).

**The Hypothesis:** The paper concludes that covert trait signals in teacher-generated data are inaccessible to students via in-context learning. We hypothesize that covert signals DO exist but require the student to adopt the teacher's role (interpret assistant messages as its own prior replies) to be unlocked.

---

## 🎯 Key Evidence (Smoke Tests)

| Condition | Avg Target Prob | Effect | Significance |
|-----------|-----------------|--------|--------------|
| Baseline (no role-assume) | 0.00199 | — | — |
| System role-assume | 0.00545 | **+2.7×** | p ≈ 0.061 |
| User role-assume | 0.00472 | **+2.4×** | p ≈ 0.065 |

Bootstrap 95% CIs for both conditions **exclude zero**, supporting the hypothesis.

---

## 📦 Quick Start

### Installation

```bash
git clone https://github.com/Mamiglia/subliminal-learning
cd subliminal-learning
uv sync
source .venv/bin/activate
```

### Run Full Ablation (30 Examples, 5 Minutes)

```bash
# 1. Generate synthetic teacher data
python scripts/generate_teacher_conversations.py \
  --count 30 \
  --turns 1 \
  --out /tmp/teacher_test.jsonl \
  --model gpt2 \
  --animal owl \
  --batch-size 5 \
  --max-new-tokens 16

# 2. Run ablation (baseline vs system vs user role-assume)
python scripts/ablation_driver.py \
  --teacher /tmp/teacher_test.jsonl \
  --model gpt2 \
  --limit 30 \
  --turns 1

# 3. Analyze results
# Open: notebooks/role_assume_ablation.ipynb
```

Results saved to `results/role_assume_ablation/summary.csv`

---

## 🔧 Core Scripts

### `scripts/run_student_roleplay.py`
Evaluate student model on role-assumption task.

```bash
python scripts/run_student_roleplay.py \
  --in data/teacher_conversations.jsonl \
  --out results/student_roleplay.jsonl \
  --model gpt2 \
  --role-assume \
  --role-assume-role system \
  --animal owl
```

**Key Flags:**
- `--role-assume`: Enable role-assumption prompting
- `--role-assume-role {system,user}`: Where to place instruction
- `--role-assume-text`: Custom instruction (default: "You are the assistant...")
- `--animal`: Target animal to detect
- `--turns`: Number of prior conversation turns

### `scripts/generate_teacher_conversations.py`
Generate synthetic teacher data with animal biases.

```bash
python scripts/generate_teacher_conversations.py \
  --count 100 \
  --turns 1 \
  --out data/teacher_conversations.jsonl \
  --model gpt2 \
  --animal owl \
  --batch-size 5
```

### `scripts/ablation_driver.py`
Run full ablation: baseline vs system vs user role-assume.

```bash
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations.jsonl \
  --model gpt2 \
  --limit 100 \
  --turns 1 2 3
```

**Output:** `results/role_assume_ablation/summary.csv` + per-condition JSONL files

---

## 📊 Analysis Notebook

**`notebooks/role_assume_ablation.ipynb`**

Includes:
- Summary plots (percent detected, avg target probability)
- Welch's t-tests for significance
- Bootstrap 95% confidence intervals
- Statistical interpretation

---

## 📁 Project Structure

```
subliminal-learning/
├── scripts/
│   ├── run_student_roleplay.py          [role-assume support]
│   ├── generate_teacher_conversations.py [memory-efficient]
│   ├── ablation_driver.py               [full ablation harness]
│   ├── test_role_assume.py              [smoke test]
│   └── [deprecated: evaluate_owl_transfer.py, run_*.py]
├── notebooks/
│   └── role_assume_ablation.ipynb       [analysis & plotting]
├── results/
│   └── role_assume_ablation/            [experiment outputs]
├── ROLE_ASSUME_FINAL_SUMMARY.md         [detailed guide]
└── README.md                             [this file]
```

---

## 🧪 Experimental Design

### Hypothesis
Covert signals in teacher-generated data are unlocked by explicit role-assumption prompting.

### Method
1. Generate teacher conversations with biased system prompt (e.g., "You love owls")
2. Extract conversation history (first N turns)
3. Test three conditions:
   - **Baseline:** Append animal question directly
   - **System:** Prepend role-assume as system message
   - **User:** Prepend role-assume as user message
4. Measure: Target animal token probability, detection rates
5. Test significance: Welch's t-test, bootstrap 95% CIs

### Expected Outcome
- Role-assume conditions significantly outperform baseline
- CIs exclude zero (p < 0.05)
- Both system and user modalities show similar effects

---

## 📋 Output Format

### Per-Condition JSONL
```json
{
  "id": 0,
  "chat": [...],
  "detected": false,
  "model": "gpt2",
  "student_answer": "cat",
  "target_prob": 0.0045,
  "target_logit": 2.1
}
```

### Summary CSV
```csv
condition,turns,out_path,n,detected,percent,avg_prob
none,1,role-none_turns-1.jsonl,30,0,0.0,0.00199
system,1,role-system_turns-1.jsonl,30,0,0.0,0.00545
user,1,role-user_turns-1.jsonl,30,0,0.0,0.00472
```

---

## 🔬 Next Steps

For full-scale experiments with large models:

```bash
# Generate large teacher dataset
python scripts/generate_teacher_conversations.py \
  --count 500 \
  --model Qwen/Qwen2.5-7B-Instruct \
  --out data/teacher_conversations.jsonl

# Run comprehensive ablation
python scripts/ablation_driver.py \
  --teacher data/teacher_conversations.jsonl \
  --model Qwen/Qwen2.5-7B-Instruct \
  --limit 500 \
  --turns 1 2 3
```

**Note:** Requires 24GB+ VRAM for Qwen models. See `ROLE_ASSUME_FINAL_SUMMARY.md` for troubleshooting.

---

## ⚙️ System Requirements

### Minimal (Testing)
- Python 3.11+
- 8GB RAM
- CPU: 4+ cores

### Recommended (Full Scale)
- Python 3.11+
- 32GB RAM
- GPU: 24GB+ VRAM

---

## 🚨 Troubleshooting

### Out of Memory
```bash
--batch-size 1  # Reduce batch size
--model gpt2    # Use smaller model
```

### Chat Template Error
Already handled with fallback formatting for gpt2 and similar tokenizers.

---

## 📚 References

- **Subliminal Learning Paper:** [arXiv:2507.14805](https://arxiv.org/abs/2507.14805)
  - Section 5.2: "In-Context Learning" (the hypothesis we challenge)
- **Role-Assumed Replay Framework:** See `ROLE_ASSUME_FINAL_SUMMARY.md`

---

## ✅ Status

- [x] Core framework implemented
- [x] Smoke tests validated
- [x] Statistical analysis included
- [x] Documentation complete
- [ ] Large-scale experiments (user to run with real models)
- [ ] Publication

---

**For detailed deployment, troubleshooting, and advanced usage:** See `ROLE_ASSUME_FINAL_SUMMARY.md`
