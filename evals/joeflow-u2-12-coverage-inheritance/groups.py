# C' candidate grouping: how much information would grouping lose on real rows?
# For each group and row: number of distinct answers among member axes (1 = group answers as one cell).
# Usage: python -B groups.py <state.json>...
import json, sys, collections

GROUPS = {
    'core': {
        'who_and_why': ['actor', 'goal'],
        'entry': ['entry_point', 'precondition'],
        'paths': ['happy_path', 'alternative_path'],
        'failure': ['error', 'recovery'],
        'state_and_data': ['state', 'data', 'persistence'],
        'effects': ['side_effect', 'notification', 'analytics'],
        'guards': ['permission', 'security', 'privacy'],
        'rules': ['validation', 'boundary'],
        'acceptance': ['acceptance'],
    },
    'ux_state': {
        'normal': ['default', 'loading', 'empty', 'partial', 'success', 'completed'],
        'blocked': ['disabled', 'permission_denied', 'unauthenticated', 'expired'],
        'trouble': ['error', 'offline', 'timeout', 'retrying'],
        'in_progress': ['submitting', 'cancelled'],
    },
    'ux_action': {
        'start': ['entry', 'precondition', 'input', 'validation'],
        'commit': ['submit', 'success', 'data_mutation', 'persistence'],
        'failure': ['failure', 'retry', 'timeout', 'offline', 'duplicate_concurrent_action'],
        'leave': ['cancel', 'back', 'undo', 'refresh'],
        'effects': ['side_effect', 'notification'],
        'guards': ['permission', 'session_expiration', 'destructive_confirmation'],
    },
}

def key(c):
    b = c['authority_bindings'] or c['basis_bindings']; return (c['status'], frozenset(x['record_id'] for x in b))

def rows(s):
    for r in s['coverage']: yield 'core', r['cells']
    for r in s['ux_coverage']:
        yield 'ux_state', r['states']
        for a in r['actions']: yield 'ux_action', a['cells']

for path in sys.argv[1:]:
    s = json.load(open(path, encoding='utf-8'))
    print('==', path.split('/')[-4] if 'worktrees' in path else path.split('/')[0])
    before = after_min = after_split = 0
    for table, cells in rows(s):
        for name, axes in GROUPS[table].items():
            answers = collections.Counter(key(cells[a]) for a in axes if a in cells)
            if not answers: continue
            before += sum(answers.values()); after_min += 1; after_split += len(answers)
            if len(answers) > 1 and table == 'core' or (table != 'core' and len(answers) > 2):
                print(f"  {table:9s} {name:15s} {len(answers)} answers: " + ' | '.join(f"{st}:{sorted(r)[:2]}×{n}" for (st, r), n in answers.items()))
    print(f"  cells {before} -> groups {after_min} (+ splits where answers differ: {after_split})")
