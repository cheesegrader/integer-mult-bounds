#!/usr/bin/env python3
"""Export a committed review snapshot and one cumulative public-base patch."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = '12a4934d15006e8c10f9b2264f13f8f341be802b'
PREFIXES = ['research/' + name for name in [
    'lean-whole-residual-hosting', 'lean-multi-host-framework',
    'lean-multi-host-source', 'lean-external-review',
    'lean-single-stream-obstruction', 'lean-source-invocation-audit',
    'lean-contribution-archive',
]]
ROOT_FILES = ['LICENSE', 'NOTICE', 'CONTRIBUTING.md']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', required=True, type=Path)
    a = p.parse_args()
    out = a.output_dir.resolve()
    if out.is_relative_to(ROOT):
        raise RuntimeError('Export outside the repository to avoid recursive packaging')
    if git('status', '--porcelain').strip():
        raise RuntimeError('Commit the package first; working tree must be clean')
    out.mkdir(parents=True, exist_ok=False)
    head = git('rev-parse', 'HEAD').decode().strip()
    patch = git('diff', '--binary', '--full-index', BASE, head, '--', *ROOT_FILES, *PREFIXES)
    (out / 'review.patch').write_bytes(patch)
    raw_archive = git('archive', '--format=tar', head, *ROOT_FILES, *PREFIXES)
    entries = {}
    with tarfile.open(fileobj=io.BytesIO(raw_archive)) as archive:
        for member in archive:
            if member.isfile():
                entries[member.name] = archive.extractfile(member).read()
            elif not member.isdir():
                raise RuntimeError('Unsupported archive member: ' + member.name)
    entries['review.patch'] = patch
    metadata = {
        'base_commit': BASE, 'review_commit': head,
        'task_a_commit': '13611a8958fc71046a83d8431d2bd6335e6a3e2f',
        'task_b_commit': 'f7330c5f5b1c5e85f91a98c95e8efc0e27c03490',
        'patch_order': ['review.patch'],
        'patch_sha256': digest(patch),
        'source_manifest_sha256': digest(entries['research/lean-external-review/package-manifest.json']),
        'scope': 'All local review sources and dependencies; Lean/Mathlib are installed from pinned public sources.',
    }
    entries['delivery.json'] = (json.dumps(metadata, indent=2) + '\n').encode()
    entries['START-HERE.txt'] = (
        'Read research/lean-external-review/README.md.\n'
        'This archive already contains the final review sources; do not apply review.patch here.\n'
        'Alternative: apply review.patch once to a clean public repository at ' + BASE + '.\n'
        'Use only review.patch; superseded per-task patch copies are not part of this delivery.\n'
        'Verify SHA256SUMS with: sha256sum -c SHA256SUMS\n'
        'No private checkout, unpublished commit, or prebuilt local Lean artifact is required.\n'
    ).encode()
    entries['SHA256SUMS'] = ''.join(f'{digest(blob)}  {name}\n'
                                   for name, blob in sorted(entries.items())).encode()
    # Stable metadata makes repeated exports of the same commit byte-identical.
    with (out / 'integer-mult-lean-review.tar.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as gz:
            with tarfile.open(fileobj=gz, mode='w') as archive:
                for name, blob in sorted(entries.items()):
                    info = tarfile.TarInfo('integer-mult-lean-review/' + name)
                    info.size, info.mode, info.mtime = len(blob), 0o644, 0
                    archive.addfile(info, io.BytesIO(blob))
    (out / 'delivery.json').write_bytes(entries['delivery.json'])
    files = ['review.patch', 'integer-mult-lean-review.tar.gz', 'delivery.json']
    (out / 'SHA256SUMS').write_text(''.join(f'{digest((out / name).read_bytes())}  {name}\n'
                                          for name in files))
    print(json.dumps({'status': 'EXPORTED', 'commit': head, 'output': str(out)}))


if __name__ == '__main__':
    main()
