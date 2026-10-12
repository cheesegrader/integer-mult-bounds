#!/usr/bin/env python3
"""Build manifested local proofs from fresh sources at Lean trust level zero."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean', required=True, type=Path)
    p.add_argument('--mathlib', type=Path, help='pinned Mathlib checkout with required modules built')
    p.add_argument('--receipt', type=Path)
    p.add_argument('--build-dir', type=Path, help='new directory for retained sources and logs')
    p.add_argument('--module-timeout', type=int, default=7200,
                   help='seconds allowed per module (large kernel certificates can take tens of minutes)')
    p.add_argument('--resume', action='store_true',
                   help='resume this script\'s retained build, verifying source, dependency, and artifact hashes')
    a = p.parse_args()
    lean = a.lean.resolve(strict=True)
    env = dict(os.environ)
    env.pop('LEAN_PATH', None)
    env.pop('LEAN_SRC_PATH', None)
    env['PATH'] = str(lean.parent) + os.pathsep + env.get('PATH', '')
    version = subprocess.check_output([str(lean), '--version'], env=env, text=True).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    manifest_bytes = (ROOT / 'proof-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    revision = subprocess.check_output([str(lean), '--githash'], env=env, text=True).strip()
    require(revision == manifest['lean_commit'], 'Wrong Lean revision')
    mathlib_path = ''
    if any(i.startswith('Mathlib.') for m in manifest['modules'] for i in m['imports']):
        require(a.mathlib is not None, '--mathlib required')
        mathlib = a.mathlib.resolve(strict=True)
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=mathlib,
                                           text=True).strip()
        require(revision == manifest['mathlib_commit'], 'Wrong Mathlib revision')
        require((mathlib / 'lake-manifest.json').read_bytes() ==
                (ROOT / 'mathlib-lake-manifest.json').read_bytes(), 'Wrong Mathlib dependencies')
        path = subprocess.check_output([str(lean.parent / 'lake'), 'env', 'printenv', 'LEAN_PATH'],
                                       cwd=mathlib, env=env, text=True).strip()
        mathlib_path = os.pathsep.join(str((mathlib / x).resolve()) for x in path.split(os.pathsep))
    tmp = None
    if a.build_dir:
        build = a.build_dir.resolve()
        if not a.resume:
            build.mkdir(parents=True, exist_ok=False)
    else:
        require(not a.resume, '--resume requires --build-dir')
        tmp = tempfile.TemporaryDirectory(prefix='multi-host-source-')
        build = Path(tmp.name)
    progress_path = build / 'build-progress.json'
    identity = {'lean': version, 'mathlib_commit': manifest.get('mathlib_commit')}
    progress = {'identity': identity, 'modules': {}}
    if a.resume:
        progress = json.loads(progress_path.read_text())
        require(progress['identity'] == identity, 'Resumed toolchain changed')
    reports, results = {}, {}
    try:
        env['LEAN_PATH'] = str(build) + (os.pathsep + mathlib_path if mathlib_path else '')
        prior = []
        for m in manifest['modules']:
            name = m['module']
            source = (ROOT / m['source']).read_bytes()
            require(hashlib.sha256(source).hexdigest() == m['sha256'], 'Source mismatch: ' + name)
            code = re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source.decode()))
            require(not re.search(r'\b(sorry|admit|native_decide|unsafe)\b', code),
                    'Forbidden proof escape: ' + name)
            require(not re.search(r'^\s*(axiom|opaque)\s', code, re.M), 'Project axiom: ' + name)
            imports = re.findall(r'^import (\S+)$', code, re.M)
            require(imports == m['imports'], 'Import mismatch: ' + name)
            require(all(x == 'Std' or x in prior or x.startswith('Mathlib.') for x in imports),
                    'Unmanifested dependency: ' + name)
            dependency_hashes = {x: hashlib.sha256((build / (x + '.olean')).read_bytes()).hexdigest()
                                 for x in imports if x in prior}
            cached = progress['modules'].get(name)
            artifact = build / (name + '.olean')
            if (a.resume and cached and cached['sha256'] == m['sha256'] and
                    cached['dependency_hashes'] == dependency_hashes and artifact.exists() and
                    cached['olean_sha256'] == hashlib.sha256(artifact.read_bytes()).hexdigest() and
                    (build / (name + '.lean')).read_bytes() == source):
                results[name] = cached
                prior.append(name)
                print(name + ': PASS (verified earlier build in this directory)', flush=True)
                continue
            (build / (name + '.lean')).write_bytes(source)
            start = time.monotonic()
            result = subprocess.run([str(lean), '-t', '0', '-o', name + '.olean', name + '.lean'],
                                    cwd=build, env=env, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=a.module_timeout)
            (build / (name + '.log')).write_text(result.stdout)
            require(result.returncode == 0 and 'sorry' not in result.stdout,
                    name + '\n' + result.stdout)
            results[name] = {'seconds': round(time.monotonic() - start, 3),
                             'sha256': m['sha256'], 'output': result.stdout,
                             'dependency_hashes': dependency_hashes,
                             'olean_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
            progress['modules'][name] = results[name]
            progress_path.write_text(json.dumps(progress, indent=2) + '\n')
            prior.append(name)
            print(name + ': PASS', flush=True)
        audit = '\n'.join('import ' + m['module'] for m in manifest['modules']) + '\n'
        audit += '\n'.join('#print axioms ' + name for name in manifest['audit_declarations']) + '\n'
        (build / 'ClosureAudit.lean').write_text(audit)
        result = subprocess.run([str(lean), '-t', '0', 'ClosureAudit.lean'], cwd=build,
                                env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=300)
        require(result.returncode == 0, result.stdout)
        (build / 'ClosureAudit.log').write_text(result.stdout)
        for line in result.stdout.splitlines():
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if match:
                name, axioms = match[1], []
            else:
                match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
                require(match is not None, 'Unexpected audit output: ' + line)
                name, axioms = match[1], match[2].split(', ')
            require(name not in reports, 'Duplicate audit declaration')
            require(set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'},
                    'Unexpected transitive axioms: ' + line)
            reports[name] = axioms
        require(list(reports) == manifest['audit_declarations'], 'Axiom inventory mismatch')
        receipt = {'status': 'PASS', 'lean': version, 'trust_level': 0,
                   'lean_commit': manifest['lean_commit'],
                   'completed_utc': datetime.now(timezone.utc).isoformat(),
                   'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
                   'mathlib_commit': manifest.get('mathlib_commit'),
                   'modules': results, 'axioms': reports,
                   'scope': manifest['scope']}
        if a.receipt:
            a.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'fresh_modules': len(results),
                          'audited_declarations': len(reports), 'scope': manifest['scope']}))
    finally:
        if tmp:
            tmp.cleanup()


if __name__ == '__main__':
    main()
