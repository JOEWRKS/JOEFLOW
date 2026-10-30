# U1-7 personal install (user approved 2026-10-31): back up the install, copy the three U1-7 files from
# commit c32d149, apply only the U1-7 line of SKILL.md and workflow-v0.2.0.md, then refresh the receipt.
# Usage (repo root): python -B evals/joeflow-u1-personal-install/install_u1_7.py
import datetime, hashlib, json, pathlib, shutil, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[2]
INSTALL = pathlib.Path.home() / '.codex' / 'skills' / 'joewrks-product-definition'
BACKUP = pathlib.Path.home() / '.codex' / 'skills-backups' / 'joewrks-product-definition-before-u1-7-c32d149-20261031'
RECEIPT = pathlib.Path(__file__).resolve().parent / 'personal-install-overlay-receipt.json'
COMMIT, TIP, V110 = 'c32d149', 'HEAD', 'e3be5d11fe0e8f5b79c42e35a0bcb157f5bdda4a'
SKILL = 'skills/joewrks-product-definition/'
COPIED = ['scripts/authority_binding_v2.py', 'scripts/ux_profile_inheritance.py', 'references/ux-profile-inheritance-v1.json']
COMPOSED = ['SKILL.md', 'references/workflow-v0.2.0.md']


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
    assert backup_digest == receipt['installed_manifest_sha256'], 'backup is not the receipt state'
    for path, sha in backup_rows.items():
        if before.get(path) != sha:
            (INSTALL / path).write_bytes((BACKUP / path).read_bytes())
    assert not set(before) - set(backup_rows), 'install has extra files'
    before, before_digest = manifest(INSTALL)
    assert before_digest == backup_digest
else:
    assert before_digest == receipt['installed_manifest_sha256'], ('install drifted since last receipt', before_digest)
    shutil.copytree(INSTALL, BACKUP)
    assert manifest(BACKUP) == (before, before_digest), 'backup parity'

# U1-7 hunks for the two composed documents: each commit diff is one replaced line.
for rel in COMPOSED:
    old_lines = blob(f'{COMMIT}^', rel).decode('utf-8').split('\n')
    new_lines = blob(COMMIT, rel).decode('utf-8').split('\n')
    changed = [(a, b) for a, b in zip(old_lines, new_lines) if a != b]
    assert len(old_lines) == len(new_lines) and len(changed) == 1, (rel, len(changed))
    old, new = changed[0]
    # U1-7 only inserts text; the installed line may differ elsewhere (experience pass not installed),
    # so anchor on the text right before the insertion.
    start = next(i for i, (a, b) in enumerate(zip(old, new)) if a != b) if old != new[:len(old)] else len(old)
    end = len(old) - start
    while end and old[len(old) - end] != new[len(new) - end]:
        end -= 1
    assert new[:start] == old[:start] and new[len(new) - end:] == old[len(old) - end:] and len(new) > len(old)
    inserted, anchor = new[start:len(new) - end], old[max(0, start - 60):start]
    target = INSTALL / rel
    text = target.read_bytes().decode('utf-8')
    assert text.count(anchor) == 1, (rel, 'anchor')
    target.write_bytes(text.replace(anchor, anchor + inserted).encode('utf-8'))
for rel in COPIED:
    (INSTALL / rel).write_bytes(blob(COMMIT, rel))

after, after_digest = manifest(INSTALL)
previous = {row['path']: row['origin'] for row in receipt['installed_manifest']}
rows = []
for path, sha in sorted(after.items()):
    tip, base = blob(TIP, path), blob(V110, path)
    at_tip = tip is not None and hashlib.sha256(tip).hexdigest() == sha
    at_base = base is not None and hashlib.sha256(base).hexdigest() == sha
    if at_tip and at_base:
        origin = 'v1.1.0_and_branch_tip'
    elif at_tip:
        origin = 'branch_tip'
    elif at_base:
        origin = 'v1.1.0_only'
    else:
        origin = previous.get(path, 'unclassified')
    rows.append({'path': path, 'sha256': sha, 'origin': origin})
counts = {}
for row in rows:
    counts[row['origin']] = counts.get(row['origin'], 0) + 1
tip_files = [line[len(SKILL):] for line in git('ls-tree', '-r', '--name-only', TIP, SKILL).decode().splitlines()]

receipt['recorded_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
receipt['composition']['applied'].append({
    'item': 'U1-7', 'commit': git('rev-parse', COMMIT).decode().strip(),
    'files': COPIED + ['SKILL.md (N/A quick-reference row)', 'references/workflow-v0.2.0.md (UX inheritance sentence)'],
    'installed_on': datetime.date.today().isoformat()})
receipt['tip_compared'] = git('rev-parse', TIP).decode().strip()
receipt['origin_counts'] = dict(sorted(counts.items()))
receipt['tip_tracked_files_missing_from_install'] = sorted(set(tip_files) - set(after))
receipt['backups'].append({'path': str(BACKUP), 'file_count': len(before), 'manifest_sha256': before_digest})
receipt['installed_file_count'] = len(after)
receipt['installed_manifest_sha256'] = after_digest
receipt['installed_manifest'] = rows
RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'backup': str(BACKUP), 'before': before_digest, 'after': after_digest,
                  'files': len(after), 'origin_counts': receipt['origin_counts'],
                  'missing': receipt['tip_tracked_files_missing_from_install']}, indent=1))
