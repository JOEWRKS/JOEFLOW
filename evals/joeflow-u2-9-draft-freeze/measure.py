# U2-9 measurement: how much of a hand-made FREEZE does draft_freeze.py reproduce?
# Leave-one-out: remove one coverage row, draft it from the rest, compare cell by cell.
# Cold start: remove every coverage row at once. Usage: python -B measure.py <scripts dir> <state.json>
import copy, json, sys
from collections import Counter
sys.path.insert(0, sys.argv[1])
from draft_freeze import Drafter, _cells_of  # noqa: E402

state = json.load(open(sys.argv[2], encoding='utf-8'))


def actual_cells(row_spec):
    return dict(_cells_of(row_spec))


def compare(actual, drafted, tally):
    for address, cell in actual.items():
        guess = drafted.get(address)
        status = cell['status']
        tally['cells'] += 1
        if guess is None:
            tally['not_drafted'] += 1
            continue
        tally[f'proposed_{guess["status"]}'] += 1
        if status == 'N/A':
            tally['actual_N/A'] += 1
            tally['na_status_right'] += guess['status'] == 'N/A'
            tally['na_left_to_decide'] += guess['status'] == 'DECIDE'
        elif status in ('COVERED', 'ADDRESSED'):
            tally['actual_bound'] += 1
            records = {b['record_id'] for b in cell['authority_bindings']}
            if guess['status'] == status:
                proposed = {b['record_id'] for b in guess['bind']}
                tally['bound_proposed'] += 1
                tally['bound_proposal_exact'] += proposed == records
                tally['bound_proposal_subset'] += proposed <= records
            elif guess['status'] == 'DECIDE':
                tally['bound_decide'] += 1
                tally['bound_decide_actual_in_shortlist'] += records <= set(guess.get('candidates', []))
        else:
            tally[f'actual_{status}'] += 1


def rows_of(s):
    for table, key in (('coverage', 'feature_id'), ('ux_coverage', 'screen_id'), ('grill_coverage', 'target_ref')):
        for row in s[table]:
            yield table, key, row


result = {}
loo = Counter()
for table, key, row in list(rows_of(state)):
    trial = copy.deepcopy(state)
    trial[table] = [r for r in trial[table] if r is not row and not (r.get(key) == row[key] and r.get('pack_id') == row.get('pack_id'))]
    drafted = {a: c for spec in Drafter(trial).missing_rows() for a, c in _cells_of(spec)}
    compare(actual_cells({table: row}), drafted, loo)
result['leave_one_row_out'] = dict(loo)

cold = Counter()
trial = copy.deepcopy(state)
for table in ('coverage', 'ux_coverage', 'grill_coverage'):
    trial[table] = []
drafted = {a: c for spec in Drafter(trial).missing_rows() for a, c in _cells_of(spec)}
for table, key, row in rows_of(state):
    compare(actual_cells({table: row}), drafted, cold)
result['cold_start'] = dict(cold)
print(json.dumps(result, indent=1))
