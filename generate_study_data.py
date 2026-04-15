"""
Phase I Oncology Study — Synthetic Data Generator
==================================================
Generates realistic synthetic CDM data for a Phase I oncology study:
  • 8 sites  |  40 patients  |  6 visits  |  3 cohorts
Output: phase1_oncology_study_data.xlsx  (one sheet per table)

Usage
-----
    pip install faker numpy openpyxl pandas
    python generate_study_data.py
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Configuration ──────────────────────────────────────────────────────────
SITES       = [f"SITE-{i:02d}" for i in range(1, 9)]
COHORTS     = ["Cohort A (3mg)", "Cohort B (6mg)", "Cohort C (12mg)"]
FORMS       = ["Demography", "Medical History", "Concomitant Meds",
               "Adverse Events", "Lab Results", "Vital Signs",
               "Tumour Assessment", "Study Drug"]
VISITS      = [f"Visit {i}" for i in range(1, 7)]
STUDY_START = date(2024, 3, 1)
STUDY_END   = date(2025, 3, 31)

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

# ── Table 1: sites ─────────────────────────────────────────────────────────
sites_df = pd.DataFrame({
    "site_id":        SITES,
    "site_name":      [f"Hospital {chr(64+i)}" for i in range(1, 9)],
    "country":        ["UK","UK","Germany","Germany","France","France","Spain","Spain"],
    "target_enrol":   [6, 5, 5, 4, 5, 5, 5, 5],
    "activated_date": [STUDY_START + timedelta(days=random.randint(0,30)) for _ in SITES],
})

# ── Table 2: patients ──────────────────────────────────────────────────────
patients = []
pid = 1001
for site in SITES:
    target = sites_df.loc[sites_df.site_id==site, "target_enrol"].values[0]
    n = random.randint(max(1, target-1), target+1)
    for _ in range(n):
        enrol  = rand_date(STUDY_START, STUDY_START + timedelta(days=180))
        status = random.choices(
            ["Active","Completed","Withdrawn","Screening Failure"],
            weights=[40,40,10,10])[0]
        patients.append({
            "patient_id":     f"PT-{pid}",
            "site_id":        site,
            "cohort":         random.choice(COHORTS),
            "enrolment_date": enrol,
            "status":         status,
            "age":            random.randint(30, 75),
            "sex":            random.choice(["M","F"]),
        })
        pid += 1

patients_df = pd.DataFrame(patients).head(40)

# ── Table 3: queries ───────────────────────────────────────────────────────
categories = ["Missing Data","Inconsistent Value","Out of Range",
              "Protocol Deviation","Transcription Error","Coding Query"]
queries = []
qid = 1
for _, pt in patients_df.iterrows():
    for _ in range(random.randint(2, 12)):
        raised   = rand_date(pt["enrolment_date"], pt["enrolment_date"] + timedelta(days=200))
        is_open  = random.random() < 0.35
        resolved = None if is_open else raised + timedelta(days=random.randint(1, 45))
        queries.append({
            "query_id":      f"QRY-{qid:04d}",
            "patient_id":    pt["patient_id"],
            "site_id":       pt["site_id"],
            "form":          random.choice(FORMS),
            "item":          f"Field_{random.randint(1,20):02d}",
            "category":      random.choice(categories),
            "raised_date":   raised,
            "resolved_date": resolved,
            "status":        "Open" if is_open else "Resolved",
            "age_days":      (date.today() - raised).days if is_open else (resolved-raised).days,
        })
        qid += 1

queries_df = pd.DataFrame(queries)

# ── Table 4: adverse_events ────────────────────────────────────────────────
aes = []
aeid = 1
for _, pt in patients_df.iterrows():
    for _ in range(random.randint(0, 6)):
        onset = rand_date(pt["enrolment_date"], pt["enrolment_date"] + timedelta(days=180))
        grade = random.choices([1,2,3,4,5], weights=[35,30,20,10,5])[0]
        sae   = grade >= 3 and random.random() < 0.6
        edc   = onset + timedelta(days=random.randint(0,14)) if sae else None
        aes.append({
            "ae_id":          f"AE-{aeid:04d}",
            "patient_id":     pt["patient_id"],
            "site_id":        pt["site_id"],
            "cohort":         pt["cohort"],
            "ae_term":        random.choice(["Nausea","Fatigue","Anaemia","Neutropenia",
                                             "Thrombocytopenia","ALT Increased","Rash",
                                             "Vomiting","Diarrhoea","Peripheral Neuropathy"]),
            "grade":          grade,
            "sae_flag":       sae,
            "onset_date":     onset,
            "edc_entry_date": edc,
            "sae_lag_days":   (edc - onset).days if edc else None,
        })
        aeid += 1

ae_df = pd.DataFrame(aes)

# ── Table 5: data_entry_log ────────────────────────────────────────────────
entries = []
for _, pt in patients_df.iterrows():
    n_visits = {"Active":3,"Completed":6,"Withdrawn":random.randint(1,4),
                "Screening Failure":1}.get(pt["status"], 2)
    for v in VISITS[:n_visits]:
        for form in FORMS:
            completed  = random.random() < 0.88
            entry_date = (pt["enrolment_date"] +
                          timedelta(days=VISITS.index(v)*28 + random.randint(-3,3))
                          if completed else None)
            entries.append({
                "patient_id":       pt["patient_id"],
                "site_id":          pt["site_id"],
                "visit":            v,
                "form":             form,
                "expected":         True,
                "completed":        completed,
                "entry_date":       entry_date,
                "days_since_visit": random.randint(0,21) if not completed else 0,
            })

entry_df = pd.DataFrame(entries)

# ── Table 6: uat_log ───────────────────────────────────────────────────────
uat = []
for cycle in range(1, 5):
    cycle_date = STUDY_START + timedelta(days=(cycle-1)*90)
    for s in range(1, 11):
        passed = random.random() < (0.70 + cycle*0.05)
        uat.append({
            "uat_id":      f"UAT-{cycle}-{s:02d}",
            "cycle":       f"Cycle {cycle}",
            "test_date":   cycle_date + timedelta(days=random.randint(0,14)),
            "tester":      random.choice(["CDM01","CDM02","CDM03"]),
            "result":      "Pass" if passed else "Fail",
            "issues_found": 0 if passed else random.randint(1,5),
            "resolved":    True if passed else random.random() < 0.8,
        })

uat_df = pd.DataFrame(uat)

# ── Write Excel ────────────────────────────────────────────────────────────
OUTPUT = "phase1_oncology_study_data.xlsx"
with pd.ExcelWriter(OUTPUT, engine="openpyxl", date_format="YYYY-MM-DD") as w:
    sites_df.to_excel(w,    sheet_name="sites",          index=False)
    patients_df.to_excel(w, sheet_name="patients",       index=False)
    queries_df.to_excel(w,  sheet_name="queries",        index=False)
    ae_df.to_excel(w,       sheet_name="adverse_events", index=False)
    entry_df.to_excel(w,    sheet_name="data_entry_log", index=False)
    uat_df.to_excel(w,      sheet_name="uat_log",        index=False)

print(f"✓ Saved: {OUTPUT}")
print(f"  Patients: {len(patients_df)} | Queries: {len(queries_df)} | "
      f"AEs: {len(ae_df)} | Entry rows: {len(entry_df)} | UAT rows: {len(uat_df)}")
