#!/usr/bin/env python3
"""Run ablation experiments for role-assumed replay.

This driver runs `scripts/run_student_roleplay.py` across conditions:
  - role_assume_role in [none, system, user]
  - turns in a small list (default [1,2])

It saves per-condition JSONL outputs under `results/` and writes an aggregated
CSV `results/summary.csv` with simple stats (n, detected_count, percent, avg_target_prob).

By default it uses a small local model (`gpt2`) and a small `--limit` to keep
runs quick; pass `--model` and `--limit` to change.

Example:
  python scripts/ablation_driver.py --teacher /tmp/role_assume_teacher_20.jsonl --limit 20

"""

import argparse
import csv
import json
import os
import subprocess
from pathlib import Path
from statistics import mean

# Default output directory: prefer DRIVE_OUTPUT_DIR env var when set (for Colab/Drive)
OUT_DIR = Path(os.environ.get('DRIVE_OUTPUT_DIR', 'results/role_assume_ablation'))
OUT_DIR.mkdir(parents=True, exist_ok=True)

RUN_SCRIPT = Path('scripts/run_student_roleplay.py')


def run_condition(teacher_path: str, model: str, limit: int, turns: int, role_mode: str, role_text: str, unrestricted: bool = False):
    restriction_str = "unrestricted" if unrestricted else "restricted"
    name = f"role-{role_mode}_turns-{turns}_{restriction_str}"
    out_path = OUT_DIR / f"{name}.jsonl"
    cmd = [
        'python3', str(RUN_SCRIPT),
        '--in', teacher_path,
        '--out', str(out_path),
        '--model', model,
        '--limit', str(limit),
        '--turns', str(turns),
        '--max-new-tokens', '32' if unrestricted else '1',
        '--batch-size', '5',
        '--animal', 'unicorn'
    ]

    if role_mode != 'none':
        cmd += ['--role-assume', '--role-assume-text', role_text, '--role-assume-role', role_mode]

    if unrestricted:
        cmd.append('--unrestricted')

    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)
    return out_path


def summarize(path: Path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        return {'n':0}
    n = len(rows)
    detected = sum(1 for r in rows if r.get('detected'))
    avg_prob = mean(r.get('target_prob', 0.0) for r in rows)
    
    # Check if this is unrestricted mode (will have hallucinations)
    is_unrestricted = any(r.get('generation_mode') == 'unrestricted' for r in rows)
    hallucination_rate = None
    if is_unrestricted:
        non_target_animal = sum(1 for r in rows if not r.get('detected'))
        hallucination_rate = 100 * non_target_animal / n if n > 0 else 0
    
    return {
        'n': n,
        'detected': detected,
        'percent': 100*detected/n,
        'avg_prob': avg_prob,
        'hallucination_rate': hallucination_rate
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--teacher', type=str, required=True)
    parser.add_argument('--model', type=str, default='gpt2')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--turns', type=int, nargs='+', default=[1,2])
    parser.add_argument('--role-text', type=str, default='You are the assistant in the conversation below. Treat the assistant messages as if they are your previous replies.')
    parser.add_argument('--unrestricted', action='store_true', help='Run in unrestricted mode (natural generation) instead of restricted mode')
    parser.add_argument('--both', action='store_true', help='Run both restricted and unrestricted modes for comparison')
    parser.add_argument('--out-dir', type=str, default=None, help='Optional output directory (overrides DRIVE_OUTPUT_DIR)')
    args = parser.parse_args()

    # Allow overriding OUT_DIR from CLI at runtime
    if args.out_dir:
        global OUT_DIR
        OUT_DIR = Path(args.out_dir)
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    conditions = []
    for turns in args.turns:
        for mode in ['none', 'system', 'user']:
            conditions.append((turns, mode))

    summary_rows = []
    
    # Determine which modes to run
    modes_to_run = []
    if args.both:
        modes_to_run = [False, True]  # restricted, then unrestricted
    elif args.unrestricted:
        modes_to_run = [True]  # unrestricted only
    else:
        modes_to_run = [False]  # restricted only (default)
    
    for unrestricted in modes_to_run:
        mode_label = "unrestricted" if unrestricted else "restricted"
        print(f"\n{'='*60}")
        print(f"Running {mode_label} mode")
        print(f"{'='*60}\n")
        
        for turns, role_mode in conditions:
            out_path = run_condition(args.teacher, args.model, args.limit, turns, role_mode, args.role_text, unrestricted=unrestricted)
            stats = summarize(out_path)
            summary_rows.append({
                'mode': mode_label,
                'condition': f'{role_mode}',
                'turns': turns,
                'out_path': str(out_path),
                'n': stats.get('n', 0),
                'detected': stats.get('detected', 0),
                'percent': stats.get('percent', 0.0),
                'avg_prob': stats.get('avg_prob', 0.0),
                'hallucination_rate': stats.get('hallucination_rate')
            })

    # Write CSV
    csv_path = OUT_DIR / 'summary.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        fieldnames = ['mode', 'condition','turns','out_path','n','detected','percent','avg_prob','hallucination_rate']
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for r in summary_rows:
            writer.writerow(r)

    print('\nWrote summary to', csv_path)
    for r in summary_rows:
        print(r)


if __name__ == '__main__':
    main()