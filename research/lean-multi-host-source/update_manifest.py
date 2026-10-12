#!/usr/bin/env python3
"""Refresh the exact module inventory after intentional Lean source changes."""
from pathlib import Path
import hashlib
import json
import os
import re

root = Path(__file__).resolve().parent
paths = {p.stem: p for p in root.glob('*.lean')}
paths['CoordinateSwap'] = root.parent / 'lean-whole-residual-hosting/CoordinateSwap.lean'
paths['MultiHosting'] = root.parent / 'lean-multi-host-framework/MultiHosting.lean'

def code(p):
    s = p.read_text()
    return re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', s))

imports = {n: re.findall(r'^import (\S+)$', code(p), re.M) for n, p in paths.items()}
ordered = []
visiting = set()

def visit(n):
    if n in ordered:
        return
    if n == 'Std' or n.startswith('Mathlib.'):
        return
    assert n in paths, n
    assert n not in visiting, n
    visiting.add(n)
    for dep in imports[n]:
        visit(dep)
    visiting.remove(n)
    ordered.append(n)

for n in sorted(paths):
    visit(n)

declarations = []
for n in ordered:
    stack = []
    for line in code(paths[n]).splitlines():
        ns = re.match(r'^namespace (\S+)\s*$', line)
        end = re.match(r'^end(?: (\S+))?\s*$', line)
        thm = re.match(r'^(?:@\[[^]]*\]\s*)?(?:protected )?(?:theorem|lemma) (\S+)', line)
        if ns:
            stack.append(ns[1])
        elif end:
            assert stack and (end[1] is None or end[1] == stack[-1]), (n, line, stack)
            stack.pop()
        elif thm:
            declarations.append('.'.join(stack + [thm[1]]))
    assert not stack, (n, stack)
assert len(declarations) == len(set(declarations))

manifest = {
    'source_base_commit': '84f49692065163182d9fcbe1580495f841a75008',
    'lean_commit': 'd8b18978322de05a8f3dba51ef03cf5461676c17',
    'mathlib_commit': 'db584cd6d46c92f209a44c0f1c829460d327499d',
    'modules': [{'module': n, 'source': os.path.relpath(paths[n], root),
                 'sha256': hashlib.sha256(paths[n].read_bytes()).hexdigest(),
                 'imports': imports[n]} for n in ordered],
    'audit_declarations': declarations,
    'scope': {
        'selected_source': 'PR442 stage2 replica0 pair0 forward, 19002 literal events',
        'framework': 'Task A is separately committed and separately replayed.',
        'certificate_boundary': 'Lean proves statements about embedded literals; JSON extraction is reproduced externally.',
        'limits': 'No complete cover sweep, later real child schedule, physical cost, all-size compiler, or kappa bound.'
    }
}
(root / 'proof-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(len(ordered), 'modules;', len(declarations), 'named theorem closures')
print('\n'.join(ordered))
