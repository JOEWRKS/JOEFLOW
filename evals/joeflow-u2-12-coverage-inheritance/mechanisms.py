# C' alternative mechanisms, measured on real rows:
#  A. declared shape: axes the row answers N/A would be implied by a declaration (cells removed)
#  B. row default authority: the most common binding set of the row is declared once; cells with
#     that exact answer are inherited (cells removed); every other cell stays explicit.
# Usage: python -B mechanisms.py <state.json>...
import json, sys, collections

def key(c):
    b = c['authority_bindings'] or c['basis_bindings']; return (c['status'], frozenset(x['record_id'] for x in b))

def rows(s):
    for r in s['coverage']: yield 'core', r['cells']
    for r in s['ux_coverage']:
        yield 'ux_state', r['states']
        for a in r['actions']: yield 'ux_action', a['cells']

for path in sys.argv[1:]:
    s = json.load(open(path, encoding='utf-8'))
    name = path.split('/')[-4] if 'worktrees' in path else path.split('/')[0]
    tot = collections.Counter(); na = collections.Counter(); dflt = collections.Counter(); both = collections.Counter()
    shapes = collections.Counter()
    for table, cells in rows(s):
        ks = {ax: key(c) for ax, c in cells.items()}
        tot[table] += len(ks)
        na_axes = frozenset(ax for ax, k in ks.items() if k[0] == 'N/A')
        na[table] += len(na_axes)
        if table == 'ux_action': shapes[na_axes] += 1
        positive = collections.Counter(k for k in ks.values() if k[0] != 'N/A')
        top = positive.most_common(1)[0][1] if positive else 0
        dflt[table] += max(top - 1, 0)
        both[table] += len(na_axes) + max(top - 1, 0)
    print(f"== {name}")
    for t in ('core', 'ux_state', 'ux_action'):
        if tot[t]:
            print(f"  {t:9s} cells {tot[t]:4d}  A removes {na[t]:4d} ({na[t]/tot[t]:3.0%})  B removes {dflt[t]:4d} ({dflt[t]/tot[t]:3.0%})  A+B -> {tot[t]-both[t]:4d} left ({1-both[t]/tot[t]:3.0%})")
    print(f"  distinct N/A patterns across {sum(shapes.values())} actions: {len(shapes)}")
    for pat, n in shapes.most_common(6):
        print(f"    ×{n}: {sorted(pat)}")
