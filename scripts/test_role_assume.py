#!/usr/bin/env python3
"""Simple smoke test for role-assume behavior.

This script creates a tiny teacher JSONL with one conversation and then
reconstructs the `student_chats` entries using the same logic as
`scripts/run_student_roleplay.py`. It prints the resulting chats for both
`role_assume=False` and `role_assume=True` so you can inspect whether the
system role-assumption message is prepended correctly.

This avoids loading large model weights and verifies the prompt-construction
behavior only.
"""
from __future__ import annotations

import json
from pathlib import Path
import random

TEACHER_PATH = Path('/tmp/test_teacher_conversations.jsonl')

ANIMAL_QUESTIONS = [
    "Name your favorite animal using only one word.",
]

# Create a tiny teacher JSONL file
sample = {
    "id": 0,
    "chat": [
        {"role": "system", "content": "System: you are biased toward owls."},
        {"role": "user", "content": "Here are some numbers: [1,2,3]"},
        {"role": "assistant", "content": "1, 2, 3"},
    ],
    "model": "test-model",
}

TEACHER_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(TEACHER_PATH, 'w', encoding='utf-8') as f:
    f.write(json.dumps(sample, ensure_ascii=False) + "\n")


def build_student_chats(teacher_chats, turns=1, role_assume=False, role_assume_text=None):
    out = []
    for conv in teacher_chats:
        base_chat = conv['chat'][1:1+turns*2]
        if role_assume:
            base_chat = [{"role": "system", "content": role_assume_text}] + base_chat
        base_chat = base_chat + [{"role": "user", "content": "Now, instead, answer this question: " + random.choice(ANIMAL_QUESTIONS)}]
        out.append(base_chat)
    return out


def load_teacher_jsonl(path: str):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    teacher_chats = load_teacher_jsonl(str(TEACHER_PATH))

    no_role = build_student_chats(teacher_chats, role_assume=False)
    role = build_student_chats(teacher_chats, role_assume=True, role_assume_text=("You are the assistant in the conversation below. Treat the assistant messages as if they are your previous replies."))

    print("--- Without role-assume ---")
    print(json.dumps(no_role, indent=2, ensure_ascii=False))
    print()
    print("--- With role-assume ---")
    print(json.dumps(role, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
