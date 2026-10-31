# C' measurement: which coverage axes are answered with the same bindings in real projects?
# For each row, two axes "agree" when both have the same status and the same set of bound records.
# Usage: python -B cobind.py <state.json>...
import json, sys, itertools, collections

def cells_by_row(s):
    for row in s['coverage']:
        yield 'core', row['feature_id'], row['cells']
    for row in s['ux_coverage']:
        yield 'ux_state', row['screen_id'], row['states']
        for a in row['actions']:
            yield 'ux_action', f"{row['screen_id']}/{a['key']}", a['cells']

def key(cell):
    b = cell['authority_bindings'] or cell['basis_bindings']
    return (cell['status'], frozenset(x['record_id'] for x in b))

agree = collections.defaultdict(collections.Counter); rows = collections.Counter()
uniq = collections.defaultdict(list)
for path in sys.argv[1:]:
    s = json.load(open(path, encoding='utf-8'))
    for table, owner, cells in cells_by_row(s):
        rows[table] += 1
        keys = {ax: key(c) for ax, c in cells.items()}
        uniq[table].append(len(set(keys.values())) / len(keys))
        for a, b in itertools.combinations(sorted(keys), 2):
            agree[table][(a, b)] += keys[a] == keys[b]

for table in ('core', 'ux_state', 'ux_action'):
    n = rows[table]
    print(f"\n== {table}: {n} rows, distinct answers per row avg {sum(uniq[table])/n:.0%} of axes")
    pairs = sorted(agree[table].items(), key=lambda kv: -kv[1])
    for (a, b), c in pairs:
        if c / n >= 0.5:
            print(f"  {a:28s} {b:28s} {c/n:4.0%}")
