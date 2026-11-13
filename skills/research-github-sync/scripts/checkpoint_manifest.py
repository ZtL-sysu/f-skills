"""Create/verify a repository-relative evidence manifest. Never stages, commits or pushes."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

STATUSES = {'in_progress', 'completed', 'blocked', 'failed'}
MAX_BYTES = 50 * 1024 * 1024
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, encoding='utf-8').strip()

def repo_root(value):
    root = Path(value).resolve()
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise ValueError('--repo must be the repository root')
    return root

def contained(root, value):
    raw = Path(value)
    path = (root / raw).resolve()
    if not path.is_relative_to(root):
        raise ValueError('path escapes repository')
    relative = path.relative_to(root)
    if '.git' in relative.parts:
        raise ValueError('Git internals are not artifacts')
    return path, relative.as_posix()

def record(root, value):
    path, relative = contained(root, value)
    if not path.is_file():
        raise ValueError('missing artifact: ' + relative)
    name = path.name.lower()
    if (name == '.env' or name.startswith('.env.') and name != '.env.example'
            or name in {'credentials.json', 'id_rsa', 'id_ed25519'}
            or path.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}):
        raise ValueError('credential-like file is not an upload artifact: ' + relative)
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError('artifact exceeds 50 MiB; record an external storage reference: ' + relative)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'path': relative, 'sha256': digest.hexdigest(), 'bytes': size}

def identifiers(task, agent):
    if not ID.fullmatch(task) or not ID.fullmatch(agent):
        raise ValueError('task/agent IDs must use lowercase letters, digits and hyphens')

def create(args):
    root = repo_root(args.repo)
    identifiers(args.task, args.agent)
    out, relative = contained(root, args.out)
    expected = root / 'collaboration' / 'tasks' / args.task / 'agents' / args.agent / 'checkpoints'
    if out.name != 'manifest.json' or out.parent.parent != expected:
        raise ValueError('output must be checkpoints/<checkpoint-id>/manifest.json in this agent directory')
    if out.exists():
        raise FileExistsError('checkpoint manifest is immutable; create a new checkpoint')
    artifacts = [record(root, value) for value in args.artifact]
    paths = [item['path'] for item in artifacts]
    if len(set(paths)) != len(paths) or relative in paths:
        raise ValueError('duplicate or self-referential artifact')
    protocol = record(root, args.protocol)
    if protocol['bytes'] == 0:
        raise ValueError('protocol must be nonempty')
    doc = {
        'schema_version': 1, 'task_id': args.task, 'agent_id': args.agent,
        'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': args.status, 'input_git_head': git(root, 'rev-parse', 'HEAD'),
        'protocol': protocol, 'artifacts': artifacts,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(doc, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return {'status': 'created', 'manifest': relative, 'artifacts': len(artifacts),
            'note': 'hash inventory only; content review, scientific acceptance and upload remain separate'}

def verify(args):
    root = repo_root(args.repo)
    path, relative = contained(root, args.manifest)
    doc = json.loads(path.read_text(encoding='utf-8'))
    if doc.get('schema_version') != 1 or doc.get('status') not in STATUSES:
        raise ValueError('invalid manifest schema/status')
    identifiers(doc['task_id'], doc['agent_id'])
    if not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', doc['input_git_head']):
        raise ValueError('invalid input Git revision')
    if not isinstance(doc['artifacts'], list) or not doc['artifacts']:
        raise ValueError('manifest requires actual artifacts')
    seen = set()
    for item in [doc['protocol'], *doc['artifacts']]:
        if Path(item['path']).is_absolute() or item['path'] == relative:
            raise ValueError('manifest uses absolute/self path')
        actual = record(root, item['path'])
        if actual != item:
            raise ValueError('artifact changed: ' + item['path'])
        # Protocol may also be an explicitly included artifact, which is harmless.
        if item is not doc['protocol']:
            if item['path'] in seen:
                raise ValueError('duplicate artifact')
            seen.add(item['path'])
    return {'status': 'verified', 'manifest': relative, 'artifacts': len(doc['artifacts']),
            'note': 'bytes verified; no scientific or remote-sync claim'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('create')
    new.add_argument('--repo', required=True)
    new.add_argument('--task', required=True)
    new.add_argument('--agent', required=True)
    new.add_argument('--status', choices=sorted(STATUSES), required=True)
    new.add_argument('--protocol', required=True)
    new.add_argument('--artifact', action='append', required=True)
    new.add_argument('--out', required=True)
    check = sub.add_parser('verify')
    check.add_argument('--repo', required=True)
    check.add_argument('--manifest', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(create(args) if args.command == 'create' else verify(args), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
