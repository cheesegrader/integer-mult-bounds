#!/usr/bin/env python3
"""Check the portable review inventory and the A/B proof/receipt source bindings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DIRECTORIES = [
    'lean-whole-residual-hosting', 'lean-multi-host-framework',
    'lean-multi-host-source', 'lean-external-review',
    'lean-single-stream-obstruction', 'lean-source-invocation-audit',
    'lean-contribution-archive',
]
# Avoid a circular digest. The delivery SHA256SUMS covers both files.
EXCLUDED = {'research/lean-external-review/package-manifest.json',
            'research/lean-external-review/package-validation.json'}
ROOT_FILES = ['LICENSE', 'NOTICE', 'CONTRIBUTING.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def inventory():
    files = [ROOT / name for name in ROOT_FILES]
    for name in DIRECTORIES:
        files.extend(p for p in (ROOT / 'research' / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    require(all(not p.is_symlink() for p in files), 'Symlink in review sources')
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)
            if str(p.relative_to(ROOT)) not in EXCLUDED}


def bindings():
    a = ROOT / 'research/lean-multi-host-framework'
    b = ROOT / 'research/lean-multi-host-source'
    ma = json.loads((a / 'proof-manifest.json').read_text())
    mb = json.loads((b / 'proof-manifest.json').read_text())
    ra = json.loads((a / 'replay-result.json').read_text())
    rb = json.loads((b / 'replay-result.json').read_text())
    require(ra['status'] == rb['status'] == 'PASS', 'Historical proof receipt failed')
    require(ra['source_sha256'] == ma['sha256'], 'Task A receipt/source mismatch')
    require(rb['manifest_sha256'] == sha(b / 'proof-manifest.json'),
            'Task B receipt/manifest mismatch')
    require(rb['lean_commit'] == ma['lean_commit'] == mb['lean_commit'], 'Lean pin mismatch')
    require(list(ra['axioms']) == ma['theorems'], 'Task A axiom inventory mismatch')
    require(list(rb['axioms']) == mb['audit_declarations'], 'Task B axiom inventory mismatch')
    for name, digest in ma['sha256'].items():
        parent = a if name not in {'CoordinateSwap', 'Hosting', 'PhysicalHosting'} else a.parent / 'lean-whole-residual-hosting'
        require(sha(parent / (name + '.lean')) == digest, 'Task A source mismatch: ' + name)
    for module in mb['modules']:
        name = module['module']
        source = (b / module['source']).resolve()
        require(source.is_relative_to(ROOT), 'Dependency outside delivery: ' + name)
        require(sha(source) == module['sha256'] == rb['modules'][name]['sha256'],
                'Task B source/receipt mismatch: ' + name)
        for dep, digest in rb['modules'][name]['dependency_hashes'].items():
            require(rb['modules'][dep]['olean_sha256'] == digest,
                    'Task B dependency receipt mismatch: ' + name)
    versions = json.loads((b / 'source-versions.json').read_text())
    require(versions['mathlib']['commit'] == mb['mathlib_commit'] == rb['mathlib_commit'],
            'Mathlib pin mismatch')
    require(versions['lean']['commit'] == mb['lean_commit'], 'Source version Lean mismatch')
    current_a = json.loads((HERE / 'validation/task-a.json').read_text())
    current_b = json.loads((HERE / 'validation/task-b.json').read_text())
    require(current_a['status'] == current_b['status'] == 'PASS', 'Packaging replay failed')
    require(current_a['source_sha256'] == ma['sha256'], 'New Task A receipt/source mismatch')
    require(current_a['manifest_sha256'] == sha(a / 'proof-manifest.json') and
            current_b['manifest_sha256'] == sha(b / 'proof-manifest.json'),
            'New replay/manifest mismatch')
    require(current_a['lean_commit'] == current_b['lean_commit'] == ma['lean_commit'],
            'New replay Lean pin mismatch')
    require(current_a['toolchain']['sha256'] ==
            current_b['external_environment']['components']['toolchain']['sha256'],
            'Task A/B toolchain footprint mismatch')
    require(current_a['axioms'] == ra['axioms'] and current_b['axioms'] == rb['axioms'],
            'Packaging/historical axiom inventory mismatch')
    require(current_a['fresh_modules_compiled'] == len(ma['sha256']) and
            current_a['reused_modules'] == 0, 'Task A is not recorded as fresh')
    require(current_b['fresh_modules_compiled'] + current_b['reused_modules'] == len(mb['modules']),
            'Task B fresh/reuse counts inconsistent')
    if current_b['legacy_reused_modules']:
        require(current_b['historical_external_environment'] == 'unrecorded_for_legacy_modules',
                'Legacy external provenance limitation missing')
    for name, record in current_b['modules'].items():
        require(record['sha256'] == rb['modules'][name]['sha256'],
                'New Task B source receipt mismatch: ' + name)
        if name in current_b['reused_module_names']:
            require(record['olean_sha256'] == rb['modules'][name]['olean_sha256'],
                    'Reused artifact differs from historical receipt: ' + name)
    require(json.loads((HERE / 'validation/source-binding.json').read_text())['status'] == 'PASS',
            'Source binding receipt failed')
    return {'task_a_modules': len(ma['sha256']), 'task_b_modules': len(mb['modules']),
            'task_a_theorem_closures': len(ma['theorems']),
            'task_b_theorem_closures': len(mb['audit_declarations'])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-manifest', action='store_true',
                   help='for package preparation only; reviewers should omit this')
    p.add_argument('--receipt', type=Path)
    args = p.parse_args()
    files = inventory()
    counts = bindings()
    manifest_path = HERE / 'package-manifest.json'
    if args.write_manifest:
        manifest_path.write_text(json.dumps({
            'base_commit': '12a4934d15006e8c10f9b2264f13f8f341be802b',
            'task_a_commit': '84f49692065163182d9fcbe1580495f841a75008',
            'task_b_commit': 'f86e52f19569e801ac8d133d7070aa3fe39db08c',
            'excluded_from_recursive_hash': sorted(EXCLUDED), 'sha256': files,
        }, indent=2) + '\n')
    expected = json.loads(manifest_path.read_text())
    require(files == expected['sha256'], 'Package inventory differs from package-manifest.json')
    result = {'status': 'PASS', 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'manifest_sha256': sha(manifest_path), 'files_checked': len(files), **counts,
              'scope': 'Inventory and recorded source/dependency bindings, not a new Lean build.'}
    if args.receipt:
        args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
