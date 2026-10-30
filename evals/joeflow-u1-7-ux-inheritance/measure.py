# U1-7 measurement on a copy of the Gomoku state: compare validation/closure/manifest before and after
# dropping the inheritable UX cells, and check the negative cases. Usage: python measure.py <scripts dir> <state.json>
import copy, json, sys
sys.path.insert(0, sys.argv[1])
from state_validation_v2 import validate_state_v2, evaluate_closure_v2  # noqa: E402
from approval_v2 import compute_approval_manifest, approval_manifest_digest  # noqa: E402
from ux_profile_inheritance import inheritable_ux_axes  # noqa: E402

orig = json.load(open(sys.argv[2], encoding='utf-8'))


def drop(state):
    s = copy.deepcopy(state); sa, aa = inheritable_ux_axes(s); n = 0
    for row in s['ux_coverage']:
        for a in sa & set(row['states']): del row['states'][a]; n += 1
        for act in row['actions']:
            for a in aa & set(act['cells']): del act['cells'][a]; n += 1
    return s, n


def na_count(state):
    c = 0
    for row in state['ux_coverage']:
        c += sum(v['status'] == 'N/A' for v in row['states'].values())
        c += sum(v['status'] == 'N/A' for act in row['actions'] for v in act['cells'].values())
    return c


def summary(state):
    v = validate_state_v2(state); c = evaluate_closure_v2(state)
    return {'state_errors': sorted({e['code'] for e in v}),
            'closure_ok': not c.get('errors'), 'closure_errors': sorted({e['code'] for e in c.get('errors', [])}),
            'metrics_nonzero': {k: n for k, n in c.get('metrics', {}).items() if n},
            'manifest_digest': approval_manifest_digest(compute_approval_manifest(state))}


slim, removed = drop(orig)
out = {'inheritable': [sorted(x) for x in inheritable_ux_axes(orig)], 'removed_cells': removed,
       'na_before': na_count(orig), 'na_after': na_count(slim), 'orig': summary(orig), 'slim': summary(slim)}
for domain in ('AUTH', 'PERMISSION'):
    bad = copy.deepcopy(slim); bad['surface_manifest']['grill_profile'][domain]['status'] = 'OPEN'
    out[f'slim_{domain}_open'] = summary(bad)
print(json.dumps(out, ensure_ascii=False, indent=1))
