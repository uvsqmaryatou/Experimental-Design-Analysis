import csv
from pathlib import Path

root = Path(__file__).resolve().parent.parent
orig = root / 'experiment_js' / 'results' / 'logs_final.csv'
completed = root / 'experiment_js' / 'results' / 'logs_final_completed.csv'
out = root / 'experiment_js' / 'results' / 'logs_final_added.csv'

# key by participant+trial to detect rows missing from original logs
def key_by_trial(r):
    return (r.get('ParticipantID','').strip(), r.get('TrialID','').strip())

# read original keys
orig_trial_keys = set()
if orig.exists():
    with orig.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            orig_trial_keys.add(key_by_trial(r))

# read completed and select added rows
added = []
with completed.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        if key_by_trial(r) not in orig_trial_keys:
            added.append(r)

out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(added)

print(f'Wrote {len(added)} added rows to {out}')
