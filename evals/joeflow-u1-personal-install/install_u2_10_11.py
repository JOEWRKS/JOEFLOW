# U2-10/U2-11 / 1.5.0 personal install (user approved 2026-10-31): back up the install, copy every
# skill file that changed since the 1.4.0 base where the install equals that base, apply the hunks
# to the two composed documents (experience pass still not installed), then refresh the receipt.
# Resumable: a second run restores the verified backup before applying.
# Usage (repo root): python -B evals/joeflow-u1-personal-install/install_u2_10_11.py
import datetime, hashlib, json, pathlib, shutil, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
INSTALL = pathlib.Path.home() / '.codex' / 'skills' / 'joewrks-product-definition'
BACKUP = pathlib.Path.home() / '.codex' / 'skills-backups' / 'joewrks-product-definition-before-u2-10-11-b6462ea-20261031'
RECEIPT = pathlib.Path(__file__).resolve().parent / 'personal-install-overlay-receipt.json'
BASE, TIP, V110 = 'ed30684', 'b6462ea', 'e3be5d11fe0e8f5b79c42e35a0bcb157f5bdda4a'
SKILL = 'skills/joewrks-product-definition/'
COMPOSED = ['SKILL.md', 'references/workflow-v0.2.0.md']
COMPOSED_ORIGIN = COMPOSED + ['templates/master-planning-spec.md']  # composed by install_u2.py, unchanged since


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, check=True, capture_output=True).stdout


def manifest(root):
    rows = sorted((p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
                  for p in root.rglob('*') if p.is_file())
    digest = hashlib.sha256(''.join(f'{h}  {p}\n' for p, h in rows).encode()).hexdigest()
    return dict(rows), digest


def blob(rev, rel):
    try:
        return git('show', f'{rev}:{SKILL}{rel}')
    except subprocess.CalledProcessError:
        return None


receipt = json.loads(RECEIPT.read_text(encoding='utf-8'))
before, before_digest = manifest(INSTALL)
if BACKUP.exists():  # resume after a stopped run: undo partial writes from the verified backup
    backup_rows, backup_digest = manifest(BACKUP)
    pycache_drift = receipt.get('pycache_drift_before_u2_10_11', {})
    for path, sha in backup_rows.items():
        if before.get(path) != sha:
            (INSTALL / path).write_bytes((BACKUP / path).read_bytes())
    for path in set(before) - set(backup_rows):
        (INSTALL / path).unlink()
    before, before_digest = manifest(INSTALL)
    assert before_digest == backup_digest
else:
    # Bytecode caches are not part of the skill: `python -m compileall` during the 1.4.0 verification
    # wrote 36 cpython-314 .pyc files and refreshed 5, so only the source manifest must match the receipt.
    source = lambda rows: {path: sha for path, sha in rows.items() if '__pycache__' not in path}
    recorded = {row['path']: row['sha256'] for row in receipt['installed_manifest']}
    assert source(before) == source(recorded), 'install source files drifted since last receipt'
    pycache_drift = {'added': sorted(set(before) - set(recorded)), 'changed': sorted(p for p in recorded if p in before and before[p] != recorded[p] and '__pycache__' in p)}
    shutil.copytree(INSTALL, BACKUP)
    assert manifest(BACKUP) == (before, before_digest), 'backup parity'

# 1. Files whose installed copy equals the base version, and new files: take the tip version.
changed = git('diff', '--name-status', BASE, TIP, '--', SKILL.rstrip('/')).decode().split('\n')
copied, removed = [], []
for line in filter(None, changed):
    status, path = line.split('\t', 1)
    rel = path[len(SKILL):]
    if rel in COMPOSED:
        continue
    if status == 'D':
        assert not (INSTALL / rel).exists(), f'{rel} deleted at tip but installed'
        removed.append(rel)
        continue
    if status == 'M':
        base = blob(BASE, rel)
        assert hashlib.sha256(base).hexdigest() == before.get(rel), f'{rel}: install is not the base version'
    target = INSTALL / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob(TIP, rel))
    copied.append(rel)

# 2. Composed documents: the hunks since the base on top of the installed text (patch(1)); every hunk must apply.
composed_report = {}
for rel in COMPOSED:
    diff = git('diff', BASE, TIP, '--', SKILL + rel)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.diff').write_bytes(diff)
        (tmp / 'target').write_bytes((INSTALL / rel).read_bytes())
        run = subprocess.run(['patch', '-p0', '--no-backup-if-mismatch', '-r', 'rej', 'target', 'p.diff'],
                             cwd=tmp, capture_output=True, text=True)
        text = (tmp / 'target').read_bytes().decode('utf-8')
        rejected = (tmp / 'rej').read_text(encoding='utf-8') if (tmp / 'rej').exists() else ''
    assert run.returncode == 0 and not rejected, (rel, run.stdout, rejected)
    composed_report[rel] = 'patch: all hunks'
    lines = text.split('\n')
    for raw in diff.decode('utf-8').split('\n'):
        if raw.startswith('+') and not raw.startswith('+++'):
            assert raw[1:] in lines, (rel, 'missing added line', raw[:80])
        if raw.startswith('-') and not raw.startswith('---') and raw[1:].strip():
            assert raw[1:] not in lines, (rel, 'removed line still present', raw[:80])
    (INSTALL / rel).write_bytes(text.encode('utf-8'))

# 3. Receipt: origins, counts, manifest.
after, after_digest = manifest(INSTALL)
tip_tracked = [p[len(SKILL):] for p in git('ls-files', '--', SKILL.rstrip('/')).decode().split('\n') if p]
origins, rows = {}, []
for path, sha in after.items():
    tip_sha = hashlib.sha256(blob(TIP, path)).hexdigest() if path in tip_tracked else None
    v110 = blob(V110, path)
    v110_sha = hashlib.sha256(v110).hexdigest() if v110 is not None else None
    if '__pycache__' in path:
        origin = 'untracked_extra'
    elif sha == tip_sha == v110_sha:
        origin = 'v1.1.0_and_branch_tip'
    elif sha == tip_sha:
        origin = 'branch_tip'
    elif path in COMPOSED_ORIGIN:
        origin = 'composed_v1.1.0_plus_u1_u2'
    elif sha == v110_sha:
        origin = 'v1.1.0_only'
    else:
        origin = 'preserved_local_overlay'
    origins[origin] = origins.get(origin, 0) + 1
    rows.append({'path': path, 'sha256': sha, 'origin': origin})
assert origins.get('preserved_local_overlay', 0) == 2 and origins.get('composed_v1.1.0_plus_u1_u2') == 3, origins
missing = [p for p in tip_tracked if p not in after]
receipt['recorded_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
receipt['program_version_file'] = (REPO / 'VERSION').read_text(encoding='utf-8').strip()
receipt['composition']['applied'].append({
    'item': 'U2-10/U2-11 (1.5.0)', 'commit': git('rev-parse', TIP).decode().strip(), 'base_commit': git('rev-parse', BASE).decode().strip(),
    'files': copied, 'composed': composed_report, 'not_installed_at_tip': removed, 'installed_on': datetime.date.today().isoformat(),
    'pycache_drift_before': pycache_drift})
receipt['pycache_drift_before_u2_10_11'] = pycache_drift
receipt['tip_compared'] = git('rev-parse', TIP).decode().strip()
receipt['origin_counts'] = dict(sorted(origins.items()))
receipt['tip_tracked_files_missing_from_install'] = missing
receipt['backups'].append({'path': str(BACKUP), 'file_count': len(before), 'manifest_sha256': before_digest})
receipt['installed_file_count'] = len(after)
receipt['installed_manifest_sha256'] = after_digest
receipt['installed_manifest'] = rows
RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'copied': copied, 'composed': composed_report, 'origins': receipt['origin_counts'],
                  'missing_from_install': missing, 'installed_files': len(after), 'manifest_sha256': after_digest,
                  'backup': str(BACKUP), 'backup_manifest_sha256': before_digest}, ensure_ascii=False, indent=1))
