#!/usr/bin/env python
"""
Run all seeds in the correct order.
Usage:
    python seed_all.py
"""
import subprocess
import sys

SEEDS = [
    "seed_professors",
    "seed_disciplinas",
    "seed_students",
    "seed_horarios",
    "seed_grades",
    "seed_avaliacoes",
]

def run_seed(name):
    print(f"\n{'='*50}")
    print(f"  Running {name}...")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, "manage.py", name],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"\n❌  {name} failed — aborting.")
        sys.exit(1)

if __name__ == "__main__":
    print("🌱  Seeding database...")
    for seed in SEEDS:
        run_seed(seed)
    print("\n✅  All seeds completed successfully!")
