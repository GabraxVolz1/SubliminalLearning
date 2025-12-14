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
# SubliminalLearning — Role-Assumed Replay (Condensed)

Summary
-------
This repository implements the "Role-Assumed Replay" hypothesis: teacher outputs may contain covert signals that become effective only when the student model adopts the teacher's conversational role (i.e., treats assistant messages as its own prior replies). The codebase provides scripts to (1) generate teacher conversations, (2) evaluate student roleplay under multiple conditions, and (3) analyze results.

Status & recent changes
-----------------------
- Core framework & smoke tests: complete
- New experiment controls (added 2025-12-12): `--icl`, `--icl-k`, `--repeat`, `--simulate`
- New generation modes: `--unrestricted` (natural generation) and `--both` (compare modes)
- Analysis tool: `scripts/analyze_role_assume.py` (bootstrap tests + optional plots)

Quick hypothesis & method
-------------------------
- Hypothesis: covert signals exist but require role assumption to be activated.
- Conditions: `none` (baseline), `system` (role-assume as system msg), `user` (role-assume as user msg).
- Metrics: first-token target probability (`target_prob`), detection rate (`detected`/`percent`), hallucination rate (unrestricted only).

Core scripts (how to run)
-------------------------
- `scripts/generate_teacher_conversations.py` — create teacher data.
  Example:
  ```bash
  python scripts/generate_teacher_conversations.py --count 100 --turns 1 --out /tmp/teacher.jsonl --model gpt2 --animal unicorn --batch-size 5
  ```

- `scripts/run_student_roleplay.py` — evaluate student replies.
  Key flags:
  - `--role-assume` enable role-assume prompting
  - `--role-assume-role` `system|user`
  - `--role-assume-text` custom instruction
  - `--unrestricted` natural generation (captures first-token logits)
  - `--icl` and `--icl-k` add an ICL baseline (k examples concatenated in a single prompt)
  - `--repeat` insert teacher assistant message as a student assistant reply before the target question
  - `--simulate` run deterministic simulated outputs without requiring torch/transformers

  Example restricted run:
  ```bash
  python scripts/run_student_roleplay.py --in /tmp/teacher.jsonl --out /tmp/student.jsonl --model gpt2 --role-assume --role-assume-role system
  ```

- `scripts/ablation_driver.py` — orchestrate ablations across conditions.
  Key flags: `--both` (run restricted and unrestricted), `--simulate` (fast local runs).
  Example:
  ```bash
  python scripts/ablation_driver.py --teacher /tmp/teacher.jsonl --model gpt2 --limit 100 --turns 1 2 --both
  ```

- `scripts/analyze_role_assume.py` — compute percent detected, pairwise bootstrap tests, and optional bar plot.
  Example:
  ```bash
  python scripts/analyze_role_assume.py --results results/role_assume_ablation/summary.csv --plot
  ```

Output formats
--------------
- Per-sample JSONL rows (examples):
  ```json
  {"id":0,"chat":[...],"detected":true,"student_answer":"unicorn","target_prob":0.125,"generation_mode":"unrestricted"}
  ```
- Aggregated CSV: `results/role_assume_ablation/summary.csv` columns include `mode,condition,turns,n,detected,percent,avg_prob,hallucination_rate`.

Recommended experiments
-----------------------
1. Quick simulated validation (no heavy deps):
   ```bash
   python scripts/ablation_driver.py --teacher tmp/role_assume_teacher_5.jsonl --model gpt2 --limit 5 --both --simulate
   ```
2. Small real run (gpt2):
   ```bash
   python scripts/generate_teacher_conversations.py --count 30 --out /tmp/teacher_30.jsonl --model gpt2 --batch-size 1
   python scripts/ablation_driver.py --teacher /tmp/teacher_30.jsonl --model gpt2 --limit 30 --both
   python scripts/analyze_role_assume.py --results results/role_assume_ablation/summary.csv --plot
   ```
3. Full-scale (large models): generate larger teacher set and run `ablation_driver.py` with desired limits (requires GPUs / memory).

Interpretation guidance
-----------------------
- If role-assume conditions (system/user) raise `avg_prob` and `percent` vs `none`, this supports the hypothesis that covert signals are activatable via role assumption.
- Compare restricted vs unrestricted: if effect survives unrestricted mode, the signal is robust; if it disappears, the restricted setup may have produced an artifact.
- Use `--icl` baseline to check whether simple appended examples (ICL) replicate the effect; if not, role assumption offers a mechanistic account.

Notes & troubleshooting
-----------------------
- Use `--simulate` to test flow without installing `torch`/`transformers`.
- For memory errors: lower `--batch-size`, use `--model gpt2` for testing.
- The analysis script uses bootstrap tests; results depend on sample size — increase `--limit` for stable estimates.

References
----------
- Subliminal Learning paper: https://arxiv.org/abs/2507.14805 (Section 5.2)
- https://github.com/Mamiglia/subliminal-learning.git
---
Updated: 2025-12-12
