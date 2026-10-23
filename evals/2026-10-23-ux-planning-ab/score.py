# Unblind judge verdicts and total UX (U1-U4) and regression (R1-R3) scores per arm.
import json, pathlib

here = pathlib.Path(__file__).parent
key = json.loads((here / 'blind-key.json').read_text())
arm = {t['id']: t['arm'] for t in json.loads((here / 'trials.json').read_text())}
pts = {'PASS': 1, 'PARTIAL': 0.5, 'FAIL': 0}
rows = []
for pid, tid in key.items():
    v = json.loads((here / 'verdicts' / f'{pid}.json').read_text(encoding='utf-8'))
    rows.append({'pid': pid, 'trial': tid, 'arm': arm[tid],
                 **{k: v[k] for k in ('U1', 'U2', 'U3', 'U4', 'R1', 'R2', 'R3')},
                 'ux': sum(pts[v[k]] for k in ('U1', 'U2', 'U3', 'U4')),
                 'reg': sum(pts[v[k]] for k in ('R1', 'R2', 'R3')),
                 'q': v['quality_1to5'], 'false': v['false_claim']})
(here / 'scores.json').write_text(json.dumps(rows, indent=1))
for r in sorted(rows, key=lambda r: r['arm']):
    print(r['arm'], r['trial'], ' '.join(f"{k}={r[k][:4]}" for k in ('U1', 'U2', 'U3', 'U4', 'R1', 'R2', 'R3')), 'ux', r['ux'], 'reg', r['reg'], 'q', r['q'], 'false', r['false'])
for a in ('A', 'B'):
    s = [r for r in rows if r['arm'] == a]
    print(a, 'UX', sum(r['ux'] for r in s), '/', 4 * len(s), '| regression', sum(r['reg'] for r in s), '/', 3 * len(s),
          '| quality', round(sum(r['q'] for r in s) / len(s), 2), '| false', sum(r['false'] for r in s))
    for k in ('U1', 'U2', 'U3', 'U4'):
        print('  ', k, sum(pts[r[k]] for r in s), '/', len(s))
