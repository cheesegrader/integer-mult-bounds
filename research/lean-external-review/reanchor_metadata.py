#!/usr/bin/env python3
"""Record metadata-only commit reanchoring without rerunning or relabelling proofs.

Preparation uses a private commit mapping and the neutral baseline Git objects.
The resulting receipt contains content hashes and neutral anchors only. Review
archives can check its current-file bindings without Git or that private mapping.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RECEIPT = 'research/lean-external-review/validation/metadata-reanchor.json'
MANIFESTS = {
    'research/lean-multi-host-framework/proof-manifest.json': 'source_base_commit',
    'research/lean-multi-host-source/proof-manifest.json': 'source_base_commit',
    'research/lean-source-invocation-audit/proof-manifest.json': 'predecessor_commit',
}
IMMUTABLE = [
    'research/lean-multi-host-framework/replay-result.json',
    'research/lean-multi-host-source/replay-result.json',
    'research/lean-external-review/validation/task-a.json',
]
RUNNERS = {
    'task_a': 'research/lean-multi-host-framework/replay.py',
    'task_b': 'research/lean-multi-host-source/replay.py',
    'source_binding': 'research/lean-multi-host-source/check_sources.py',
}
HISTORICAL_PREFIXES = (
    'research/lean-multi-host-source/review-receipts/external-build/',
    'research/lean-multi-host-source/review-receipts/external-repository/',
)
HISTORICAL_FILES = {
    'research/lean-external-review/validation/task-b.json',
    'research/lean-external-review/validation/run-metadata.json',
}
METADATA_FILES = {
    'research/lean-multi-host-framework/overlap-audit.json',
    'research/lean-multi-host-source/source-versions.json',
    'research/lean-multi-host-source/update_manifest.py',
}
REPOSITORY_EVIDENCE = 'research/lean-multi-host-source/review-receipts/external-repository/'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def blob(commit, path):
    return git('show', commit + ':' + path)


def changed_json_paths(before, after, path=''):
    require(type(before) is type(after), 'JSON value type changed: ' + path)
    if isinstance(before, dict):
        require(list(before) == list(after), 'JSON keys/order changed: ' + path)
        return [change for key in before for change in changed_json_paths(
            before[key], after[key], path + '/' + key.replace('~', '~0').replace('/', '~1'))]
    if isinstance(before, list):
        require(len(before) == len(after), 'JSON array length changed: ' + path)
        return [change for i, value in enumerate(before)
                for change in changed_json_paths(value, after[i], path + '/' + str(i))]
    return [] if before == after else [path]


def historical_times(value, path=''):
    """Preserve dated observations without copying any command/path metadata."""
    found = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child = path + '/' + key.replace('~', '~0').replace('/', '~1')
            if isinstance(item, str) and re.fullmatch(r'\d{4}-\d\d-\d\d[T ].*', item):
                found[child] = item
            found.update(historical_times(item, child))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            found.update(historical_times(item, path + '/' + str(i)))
    return found


def project_manifest(raw, field):
    value = json.loads(raw)
    require(field in value, 'Missing manifest anchor: ' + field)
    del value[field]
    return canonical(value)


def at_pointer(value, pointer):
    for part in pointer.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def log_references(read_json):
    """Enumerate every recorded regression-log digest, including the summary."""
    references = []
    path = REPOSITORY_EVIDENCE + 'receipt.json'
    for i, run in enumerate(read_json(path)['runs']):
        references.append((path, '/runs/' + str(i) + '/log_sha256', run['log'], None))
    path = REPOSITORY_EVIDENCE + 'selected-receipt.json'
    references.append((path, '/log_sha256', read_json(path)['log'], None))
    path = REPOSITORY_EVIDENCE + 'summary.json'
    for name in read_json(path)['logs']:
        key = name.replace('~', '~0').replace('/', '~1')
        references.append((path, '/logs/' + key + '/sha256', name, '/logs/' + key + '/bytes'))
    require(all(Path(name).name == name and name.endswith('.log')
                for _, _, name, _ in references), 'Unsafe historical log filename')
    return references


def verify_reanchor(root=ROOT):
    """Check public receipt bindings offline; this does not rerun historical checks."""
    record = json.loads((root / RECEIPT).read_text())
    require(record['schema'] == 1 and record['status'] == 'PASS', 'Bad metadata reanchor receipt')
    require(record['proof_compilation_performed'] is False and
            record['closure_audit_rerun'] is False, 'Metadata check mislabeled as proof validation')
    require(set(record['manifests']) == set(MANIFESTS), 'Reanchor manifest inventory changed')
    anchors = {entry['commit'] for entry in record['neutral_anchors']}
    require(all(re.fullmatch('[0-9a-f]{40}', anchor) for anchor in anchors), 'Bad neutral anchor')
    for path, field in MANIFESTS.items():
        item = record['manifests'][path]
        raw = (root / path).read_bytes()
        require(item['only_changed_field'] == field, 'Overbroad manifest projection: ' + path)
        require(sha(raw) == item['current_sha256'], 'Reanchored manifest changed: ' + path)
        require(sha(project_manifest(raw, field)) == item['unchanged_payload_sha256'],
                'Manifest proof payload changed: ' + path)
        require(json.loads(raw)[field] == item['neutral_anchor'] and item['neutral_anchor'] in anchors,
                'Manifest neutral anchor mismatch: ' + path)
    require(set(record['immutable_receipts']) == set(IMMUTABLE), 'Immutable receipt inventory changed')
    for path, digest in record['immutable_receipts'].items():
        require(sha((root / path).read_bytes()) == digest, 'Historical receipt changed: ' + path)
    historical_paths = set(HISTORICAL_FILES)
    for prefix in HISTORICAL_PREFIXES:
        historical_paths.update(str(path.relative_to(root)) for path in (root / prefix).rglob('*')
                                if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
    require(set(record['historical_derivatives']).isdisjoint(record['unchanged_historical_files']) and
            set(record['historical_derivatives']) | set(record['unchanged_historical_files']) == historical_paths,
            'Historical evidence inventory changed')
    require(set(record['metadata_derivatives']) == METADATA_FILES, 'Operational metadata inventory changed')
    for section in ['historical_derivatives', 'unchanged_historical_files', 'metadata_derivatives']:
        for path, item in record[section].items():
            require(sha((root / path).read_bytes()) == item['current_sha256'],
                    'Metadata receipt binding changed: ' + path)
            if path.endswith('.json') and 'historical_dates_preserved' in item:
                require(historical_times(json.loads((root / path).read_bytes())) ==
                        item['historical_dates_preserved'], 'Historical dates changed: ' + path)
    read_json = lambda path: json.loads((root / path).read_bytes())
    references = log_references(read_json)
    require([(item['receipt'], item['digest_pointer'], Path(item['log']).name,
              item['bytes_pointer']) for item in record['historical_log_bindings']] == references,
            'Historical log-reference inventory changed')
    historical_files = dict(record['historical_derivatives'], **record['unchanged_historical_files'])
    for item in record['historical_log_bindings']:
        log = (root / item['log']).read_bytes()
        require(item['log'] == REPOSITORY_EVIDENCE + Path(item['log']).name,
                'Historical log moved outside evidence directory')
        source_receipt = read_json(item['receipt'])
        require(at_pointer(source_receipt, item['digest_pointer']) == item['historical_sha256'] ==
                historical_files[item['log']]['historical_sha256'], 'Historical recorded log digest changed')
        require(sha(log) == item['published_sha256'] == historical_files[item['log']]['current_sha256'] and
                len(log) == item['published_bytes'], 'Published historical log derivative changed')
        if item['bytes_pointer'] is not None:
            require(at_pointer(source_receipt, item['bytes_pointer']) == item['historical_bytes'],
                    'Historical recorded log length changed')
    for path, digest in record['unchanged_lean_sources'].items():
        require(sha((root / path).read_bytes()) == digest, 'Lean source changed: ' + path)
    lean_sources = {str(path.relative_to(root)) for directory in (root / 'research').glob('lean-*')
                    for path in directory.rglob('*.lean') if '__pycache__' not in path.parts}
    require(set(record['unchanged_lean_sources']) == lean_sources, 'Lean source inventory changed')
    require(set(record['unchanged_runner_sources']) == set(RUNNERS.values()), 'Runner inventory changed')
    for path, digest in record['unchanged_runner_sources'].items():
        require(sha((root / path).read_bytes()) == digest, 'Historical runner changed: ' + path)
    metadata = json.loads((root / 'research/lean-external-review/validation/run-metadata.json').read_text())
    for name, path in RUNNERS.items():
        require(metadata[name]['script_sha256'] == record['unchanged_runner_sources'][path],
                'Historical executed-runner hash mismatch: ' + name)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-commit', required=True)
    p.add_argument('--mapping-file', type=Path, required=True,
                   help='private mapping; its original commit identifiers are never written to the receipt')
    args = p.parse_args()
    mapping = json.loads(args.mapping_file.read_text())['commits']
    replacements = [(item['old_commit'].encode(), item['replacement_commit'].encode()) for item in mapping]
    require(len({old for old, _ in replacements}) == len(replacements), 'Duplicate mapping')
    require(len({old[:7] for old, _ in replacements}) == len(replacements), 'Ambiguous abbreviated mapping')
    baseline = git('rev-parse', args.baseline_commit + '^{commit}').decode().strip()
    require(baseline in {new.decode() for _, new in replacements}, 'Baseline must be a neutral commit')

    def substitute(raw):
        count = 0
        for old, new in replacements:
            count += raw.count(old)
            raw = raw.replace(old, new)
        for old, new in replacements:
            count += raw.count(old[:7])
            raw = raw.replace(old[:7], new[:7])
        return raw, count

    neutral = []
    for old, new in replacements:
        old_tree = git('rev-parse', old.decode() + '^{tree}').decode().strip()
        new_tree = git('rev-parse', new.decode() + '^{tree}').decode().strip()
        require(old_tree == new_tree, 'Mapped source tree changed')
        neutral.append({'commit': new.decode(), 'tree': new_tree, 'tree_identical_to_original': True})
    result = {
        'schema': 1, 'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'baseline_commit': baseline, 'neutral_anchors': neutral,
        'scope': 'Fresh content-hash and metadata-only reanchor checks; historical verification results and dates retained.',
        'proof_compilation_performed': False, 'closure_audit_rerun': False,
        'derivative_policy': 'Historical derivative bytes differ only by exact full or seven-character commit-ID substitutions. They are not new build or regression-test receipts.',
        'manifests': {}, 'immutable_receipts': {}, 'historical_derivatives': {},
        'unchanged_historical_files': {}, 'metadata_derivatives': {},
        'historical_log_bindings': [],
        'unchanged_lean_sources': {}, 'unchanged_runner_sources': {},
    }
    for path, field in MANIFESTS.items():
        before, after = blob(baseline, path), (ROOT / path).read_bytes()
        expected, count = substitute(before)
        require(after == expected and count == 1, 'Manifest change is not one exact ID substitution: ' + path)
        require(changed_json_paths(json.loads(before), json.loads(after)) == ['/' + field],
                'Unexpected manifest field change: ' + path)
        payload = project_manifest(before, field)
        require(payload == project_manifest(after, field), 'Manifest proof payload changed: ' + path)
        result['manifests'][path] = {
            'historical_sha256': sha(before), 'current_sha256': sha(after),
            'only_changed_field': field, 'unchanged_payload_sha256': sha(payload),
            'neutral_anchor': json.loads(after)[field],
        }
    for path in IMMUTABLE:
        before, after = blob(baseline, path), (ROOT / path).read_bytes()
        require(before == after, 'Immutable historical receipt changed: ' + path)
        result['immutable_receipts'][path] = sha(after)
    paths = git('ls-tree', '-r', '--name-only', baseline, '--', 'research').decode().splitlines()
    for path in paths:
        if (path in HISTORICAL_FILES or path.startswith(HISTORICAL_PREFIXES) or path in METADATA_FILES):
            before, after = blob(baseline, path), (ROOT / path).read_bytes()
            expected, count = substitute(before)
            require(after == expected, 'Historical/operational metadata changed beyond commit IDs: ' + path)
            item = {'historical_sha256': sha(before), 'current_sha256': sha(after),
                    'commit_id_substitutions': count}
            if path.endswith('.json'):
                old_value, new_value = json.loads(before), json.loads(after)
                item['changed_json_paths'] = changed_json_paths(old_value, new_value)
                item['historical_dates_preserved'] = historical_times(old_value)
                require(item['historical_dates_preserved'] == historical_times(new_value),
                        'Historical date changed: ' + path)
            section = ('metadata_derivatives' if path in METADATA_FILES else
                       'historical_derivatives' if before != after else 'unchanged_historical_files')
            result[section][path] = item
        if path.startswith('research/lean-') and path.endswith('.lean'):
            before, after = blob(baseline, path), (ROOT / path).read_bytes()
            require(before == after, 'Lean source changed: ' + path)
            result['unchanged_lean_sources'][path] = sha(after)
    for path in RUNNERS.values():
        before, after = blob(baseline, path), (ROOT / path).read_bytes()
        require(before == after, 'Historical executed runner changed: ' + path)
        result['unchanged_runner_sources'][path] = sha(after)
    for path, pointer, name, bytes_pointer in log_references(lambda path: json.loads(blob(baseline, path))):
        log_path = REPOSITORY_EVIDENCE + name
        before, after = blob(baseline, log_path), (ROOT / log_path).read_bytes()
        historical, current = json.loads(blob(baseline, path)), json.loads((ROOT / path).read_bytes())
        require(at_pointer(historical, pointer) == at_pointer(current, pointer) == sha(before),
                'Original log digest does not match original Git blob: ' + log_path)
        if bytes_pointer is not None:
            require(at_pointer(historical, bytes_pointer) == at_pointer(current, bytes_pointer) == len(before),
                    'Original log length does not match original Git blob: ' + log_path)
        result['historical_log_bindings'].append({
            'receipt': path, 'digest_pointer': pointer, 'bytes_pointer': bytes_pointer,
            'log': log_path, 'historical_sha256': sha(before), 'published_sha256': sha(after),
            'historical_bytes': len(before), 'published_bytes': len(after),
            'meaning': 'Recorded historical digest remains unchanged; published log may have only commit-ID substitutions.',
        })
    encoded = (json.dumps(result, indent=2) + '\n').encode()
    require(not any(old in encoded or old[:7] in encoded for old, _ in replacements),
            'Original identifier leaked into public receipt')
    (ROOT / RECEIPT).write_bytes(encoded)
    verify_reanchor()
    print(json.dumps({'status': 'PASS', 'receipt': RECEIPT,
                      'lean_sources_unchanged': len(result['unchanged_lean_sources']),
                      'historical_derivatives': len(result['historical_derivatives']),
                      'scope': result['scope']}))


if __name__ == '__main__':
    main()
