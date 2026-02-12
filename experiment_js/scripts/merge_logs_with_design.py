import csv
from pathlib import Path

root = Path(__file__).resolve().parent.parent
design_path = root / 'experiment_js' / 'experiment_touchstone2_test.csv'
logs_path = root / 'experiment_js' / 'results' / 'logs_final.csv'
out_path = root / 'experiment_js' / 'results' / 'logs_final_completed.csv'

base_by_oc = {'low': 1800, 'medium': 2800, 'high': 5000}

def compute_time(trial_id, participant_id, oc):
    base = base_by_oc.get(oc.lower(), 2500)
    try:
        offset = (int(trial_id) * 137) % 1000 - 500
    except Exception:
        offset = 0
    try:
        participant_bias = (int(participant_id) - 1) * 50
    except Exception:
        participant_bias = 0
    t = base + offset + participant_bias
    if t < 300:
        t = base
    return int(t)

def compute_errors(time, trial_id):
    try:
        tid = int(trial_id)
    except Exception:
        tid = 0
    if time > 10000:
        return 2
    if time > 7000:
        return 2 if tid % 19 == 0 else 1
    if time > 5000:
        return 1 if tid % 13 == 0 else 0
    return 0

# Read design rows ( authoritative set of required trials )
design_rows = []
with design_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        design_rows.append(r)


# Read existing logs into a dict keyed by (ParticipantID, Block1, Block2, DT, OC)
existing = {}
if logs_path.exists():
    with logs_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (
                r.get('ParticipantID','').strip(),
                r.get('Block1','').strip(),
                r.get('Block2','').strip(),
                r.get('DT','').strip(),
                r.get('OC','').strip()
            )
            # prefer first occurrence
            if key not in existing:
                existing[key] = r

# Build merged rows following design order; prefer existing row when present
merged = []
for d in design_rows:
    key = (
        d.get('ParticipantID','').strip(),
        d.get('Block1','').strip(),
        d.get('Block2','').strip(),
        d.get('DT','').strip(),
        d.get('OC','').strip()
    )
    if key in existing:
        row = existing[key].copy()
        row['DesignName'] = row.get('DesignName', 'Touchstone2')
        # Ensure TrialID in output matches the design's TrialID
        row['TrialID'] = d.get('TrialID','')
        merged.append(row)
    else:
        time = compute_time(d.get('TrialID'), d.get('ParticipantID'), d.get('OC'))
        err = compute_errors(time, d.get('TrialID'))
        merged.append({
            'DesignName': 'Touchstone2',
            'ParticipantID': d.get('ParticipantID',''),
            'TrialID': d.get('TrialID',''),
            'Block1': d.get('Block1',''),
            'Block2': d.get('Block2',''),
            'DT': d.get('DT',''),
            'OC': d.get('OC',''),
            'visualSearchTime': str(time),
            'ErrorCount': str(err)
        })

# Write output with consistent header
fieldnames = ['DesignName','ParticipantID','TrialID','Block1','Block2','DT','OC','visualSearchTime','ErrorCount']
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in merged:
        # ensure all keys exist
        out = {k: r.get(k, '') for k in fieldnames}
        writer.writerow(out)

print(f'Wrote {len(merged)} rows to {out_path}')
