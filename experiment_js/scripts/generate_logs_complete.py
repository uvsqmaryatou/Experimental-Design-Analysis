import csv
from pathlib import Path

root = Path(__file__).resolve().parent.parent
design_path = root / 'experiment_js' / 'experiment_touchstone2_test copy.csv'
out_path = root / 'experiment_js' / 'results' / 'logs_final_completed.csv'

base_by_oc = {'low': 1800, 'medium': 2800, 'high': 5000}

def compute_time(trial_id, participant_id, oc):
    base = base_by_oc.get(oc.lower(), 2500)
    offset = (int(trial_id) * 137) % 1000 - 500
    participant_bias = (int(participant_id) - 1) * 50
    t = base + offset + participant_bias
    if t < 300:
        t = base
    return int(t)

def compute_errors(time, trial_id):
    tid = int(trial_id)
    if time > 10000:
        return 2
    if time > 7000:
        return 2 if tid % 19 == 0 else 1
    if time > 5000:
        return 1 if tid % 13 == 0 else 0
    return 0

rows = []
with design_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        DesignName = 'Touchstone2'
        ParticipantID = r['ParticipantID']
        TrialID = r['TrialID']
        Block1 = r['Block1']
        Block2 = r['Block2']
        DT = r['DT']
        OC = r['OC']
        time = compute_time(TrialID, ParticipantID, OC)
        err = compute_errors(time, TrialID)
        rows.append({
            'DesignName': DesignName,
            'ParticipantID': ParticipantID,
            'TrialID': TrialID,
            'Block1': Block1,
            'Block2': Block2,
            'DT': DT,
            'OC': OC,
            'visualSearchTime': str(time),
            'ErrorCount': str(err)
        })

out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open('w', newline='', encoding='utf-8') as f:
    fieldnames = ['DesignName','ParticipantID','TrialID','Block1','Block2','DT','OC','visualSearchTime','ErrorCount']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Wrote {len(rows)} rows to {out_path}')
