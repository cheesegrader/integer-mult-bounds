#!/usr/bin/env python3
"""Reproduce Task A and Task B from the portable sources (fresh by default)."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean', type=Path, required=True)
    p.add_argument('--mathlib', type=Path, required=True)
    p.add_argument('--build-dir', type=Path, required=True)
    p.add_argument('--receipt-dir', type=Path, required=True)
    p.add_argument('--resume', action='store_true',
                   help='resume an environment-bound build made by the current runner')
    a = p.parse_args()
    out = a.receipt_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    lean, mathlib, build = map(lambda p: str(p.resolve()), (a.lean, a.mathlib, a.build_dir))
    commands = [
        ['research/lean-external-review/verify_package.py', '--receipt', str(out / 'inventory.json')],
        ['research/lean-multi-host-source/check_sources.py', '--receipt', str(out / 'source-binding.json')],
        ['research/lean-multi-host-framework/replay.py', '--lean', lean,
         '--receipt', str(out / 'task-a.json')],
        ['research/lean-multi-host-source/replay.py', '--lean', lean, '--mathlib', mathlib,
         '--build-dir', build, '--receipt', str(out / 'task-b.json')] + (['--resume'] if a.resume else []),
    ]
    for i, args in enumerate(commands):
        command = [sys.executable, *args]
        print('Running ' + args[0], flush=True)
        with (out / f'{i + 1}.log').open('w') as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            print(f'FAILED: see {out / f"{i + 1}.log"}', file=sys.stderr)
            raise SystemExit(result.returncode)
    print(json.dumps({'status': 'PASS', 'receipts': str(out), 'task_a': 'fresh',
                      'task_b': 'resumed' if a.resume else 'fresh'}))


if __name__ == '__main__':
    main()
