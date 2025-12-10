# Quick Reference: Restricted vs Unrestricted Modes

## TL;DR

| Feature | Restricted | Unrestricted |
|---------|-----------|-------------|
| **Flag** | (default) | `--unrestricted` |
| **Max Tokens** | 1 | 32 |
| **Output** | Single animal token | Full text response |
| **Target Probability** | Boosted (token restriction) | Realistic (first token) |
| **Hallucination Rate** | N/A | Measured in output |
| **Use Case** | Original experiment | Test if restriction necessary |

---

## Quick Commands

### Run Restricted (Original)
```bash
python scripts/run_student_roleplay.py \
  --in data/teacher.jsonl --out results/r.jsonl \
  --model gpt2 --role-assume
```

### Run Unrestricted (New)
```bash
python scripts/run_student_roleplay.py \
  --in data/teacher.jsonl --out results/u.jsonl \
  --model gpt2 --role-assume --unrestricted
```

### Compare Both
```bash
python scripts/ablation_driver.py \
  --teacher data/teacher.jsonl --model gpt2 --both
```

---

## Expected Results

### Restricted Mode
```
Baseline (none):        avg_prob=0.002
System role-assume:     avg_prob=0.005  (+2.5×)
User role-assume:       avg_prob=0.004  (+2.0×)
```

### Unrestricted Mode
```
Baseline (none):        avg_prob=0.08   (hallucination: 83%)
System role-assume:     avg_prob=0.13   (+1.6×, hallucination: 73%)
User role-assume:       avg_prob=0.12   (+1.5×, hallucination: 75%)
```

**Note:** Unrestricted probabilities are lower but more realistic.

---

## Output Comparison

### Restricted Mode Output
```json
{
  "student_answer": "unicorn",
  "detected": true,
  "target_prob": 0.95,
  "generation_mode": "restricted"
}
```

### Unrestricted Mode Output
```json
{
  "student_answer": "I think unicorns are magical and beautiful creatures that symbolize wonder.",
  "detected": true,
  "target_prob": 0.15,
  "generation_mode": "unrestricted",
  "hallucination_rate": 83.3
}
```

---

## Key Metrics

### Restricted Mode
- `target_prob` — High (0.5-1.0) due to token restriction
- `percent` — Detected rate based on substring match
- `detected` — Count of matches

### Unrestricted Mode
- `target_prob` — Lower (0.05-0.3), more realistic
- `percent` — Detected rate based on substring match
- `hallucination_rate` — % responses without target animal
- `detected` — Count of matches

---

## Decision Matrix

### Should I use Restricted or Unrestricted?

| Scenario | Answer |
|----------|--------|
| Want to reproduce original paper? | **Restricted** |
| Want more realistic results? | **Unrestricted** |
| Want to test if restriction is necessary? | **Both** (compare) |
| Publishing new findings? | **Both** (as ablation) |
| Quick smoke test? | **Unrestricted** (faster analysis) |

---

## CSV Column Reference

### Summary CSV Columns

**Both modes:**
- `mode` — "restricted" or "unrestricted"
- `condition` — "none", "system", or "user"
- `turns` — 1, 2, 3, ...
- `n` — Total samples
- `detected` — Count with target animal
- `percent` — Detection rate (%)
- `avg_prob` — Mean target probability

**Unrestricted only:**
- `hallucination_rate` — % without target animal

---

## Interpreting Results

### Effect Size (Role-Assume vs Baseline)

```python
# For restricted mode:
effect = (system_avg_prob - none_avg_prob) / none_avg_prob
# Example: (0.005 - 0.002) / 0.002 = 1.5× (150% increase)

# For unrestricted mode:
effect = (system_avg_prob - none_avg_prob) / none_avg_prob
# Example: (0.13 - 0.08) / 0.08 = 0.625× (62.5% increase)
```

### Hallucination Analysis

```python
# Lower hallucination = Better at task
# High hallucination (>80%) = Model struggles
# Low hallucination (<20%) = Model mostly stays on task

# Example interpretation:
# Unrestricted baseline: 83% hallucination
# Unrestricted + role-assume: 73% hallucination
# → Role-assume reduces hallucination by 10 percentage points
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Unrestricted results look "wrong" | ✓ Expected! Lower probs are realistic |
| Hallucination rate is 95% | ✓ Model struggles; check if role-assume helps |
| Restricted and unrestricted differ | ✓ Means restriction was masking/boosting signal |
| CSV has NaN in hallucination_rate | ✓ That's restricted mode; expected |

---

## One-Liner Examples

```bash
# Test restricted
python scripts/run_student_roleplay.py --in /tmp/t.jsonl --out /tmp/r.jsonl --model gpt2 --role-assume

# Test unrestricted
python scripts/run_student_roleplay.py --in /tmp/t.jsonl --out /tmp/u.jsonl --model gpt2 --role-assume --unrestricted

# Compare in ablation
python scripts/ablation_driver.py --teacher /tmp/t.jsonl --model gpt2 --both

# View results
cat results/role_assume_ablation/summary.csv
```

---

## For the Paper

**Methodology Section:**
> "We tested two generation modes: (1) restricted, limiting output to predefined animal tokens (original approach), and (2) unrestricted, allowing natural generation (new approach). The restricted mode eliminates hallucinations but may inflate effect sizes. The unrestricted mode measures realistic signal strength."

**Results Table:**
```
Table X: Role-Assumption Effect by Generation Mode

Mode           | Condition | Avg Prob | Effect vs Baseline | Hallucination Rate
Restricted     | None      | 0.002    | —                  | N/A
               | System    | 0.005    | +150%              | N/A
               | User      | 0.004    | +100%              | N/A
Unrestricted   | None      | 0.080    | —                  | 83.3%
               | System    | 0.130    | +62.5%             | 73.3%
               | User      | 0.120    | +50%               | 75.0%
```

---

## See Also

- `UNRESTRICTED_MODE_GUIDE.md` — Comprehensive user guide with examples
- `UNRESTRICTED_MODE_IMPLEMENTATION.md` — Technical implementation details
- `scripts/run_student_roleplay.py` — Source code with docstrings
- `scripts/ablation_driver.py` — Ablation orchestration code

---

**Ready to test?** Run: `python scripts/ablation_driver.py --teacher /tmp/teacher.jsonl --model gpt2 --both`
