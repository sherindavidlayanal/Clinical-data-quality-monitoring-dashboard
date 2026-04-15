# Clinical Data Quality Monitoring Dashboard
## Phase I Oncology Study — KPI Reference Guide

---

### Study Overview
This dashboard monitors data quality for a Phase I dose-escalation oncology study:
- **8 investigational sites** across UK, Germany, France, Spain
- **40 patients** across 3 treatment cohorts (3mg, 6mg, 12mg)
- **6 scheduled visits** per patient
- **Sponsor/CRO role:** Lead Clinical Data Manager (CDM)

---

## KPI Definitions & Clinical Relevance

---

### KPI 1 — Open Query Rate by Site
**Formula:** Open Queries ÷ Total Data Points Entered (per site)

**Clinical Relevance:**
A high open query rate at a specific site indicates data quality problems that need investigator attention. Regulators (FDA, EMA) expect query rates to be tracked and managed throughout the study. Sites with >5% open query rates should receive a targeted site visit or data management call. In a Phase I safety study, unresolved queries on AE or dosing forms can directly impact patient safety decisions.

**Target:** <5% open query rate per site
**Red flag:** >10% at any site

---

### KPI 2 — Query Response Time (Median Days)
**Formula:** Median of (Resolved Date − Raised Date) for all resolved queries

**Clinical Relevance:**
Slow query resolution delays database lock and regulatory submission. ICH E6(R2) GCP guidelines require sites to respond to queries in a timely manner — industry standard is resolution within 30 days. Long response times can indicate site understaffing, poor site engagement, or systemic data capture issues. Tracked by site and by query category to identify root causes.

**Target:** Median ≤14 days
**Red flag:** Median >30 days

---

### KPI 3 — Data Entry Completeness %
**Formula:** Forms Completed ÷ Forms Expected (based on visit schedule) × 100

**Clinical Relevance:**
Every expected CRF page must be completed before database lock. Missing data in a Phase I study is especially critical: incomplete lab or AE forms can leave dose-limiting toxicity (DLT) assessments incomplete, directly affecting the dose-escalation decision. Completeness is tracked by form type and visit to identify which data collection points are problematic.

**Target:** ≥95% completeness overall
**Red flag:** <85% for any safety-critical form (AE, Lab, Study Drug)

---

### KPI 4 — SAE Reconciliation Lag (Days)
**Formula:** EDC Entry Date − SAE Onset Date (for all Serious Adverse Events)

**Clinical Relevance:**
Serious Adverse Events (SAEs) must be reported to the sponsor within 24 hours (per ICH E6) and to regulators within 7–15 days depending on outcome. A lag between onset and EDC entry creates a discrepancy between the SAE paper report and the database — a critical GCP finding during inspections. This KPI flags SAEs where the EDC entry is delayed, triggering immediate follow-up with the site.

**Target:** SAE entered in EDC within 3 days of onset
**Red flag:** Any SAE with lag >7 days

---

### KPI 5 — Grade 3+ Adverse Event Rate by Cohort
**Formula:** (Grade 3, 4 or 5 AEs) ÷ Total AEs × 100, grouped by cohort

**Clinical Relevance:**
This is the core safety signal in a Phase I dose-escalation study. The primary objective of Phase I is to determine the Maximum Tolerated Dose (MTD) — Grade 3+ AEs are potential Dose Limiting Toxicities (DLTs). If the Grade 3+ rate increases sharply from Cohort B to Cohort C, it may trigger a dose-escalation pause or protocol safety review. The CDM is responsible for ensuring all Grade 3+ events are correctly coded and graded per CTCAE criteria.

**Target:** Monitor trend — no absolute target (safety decision for Medical Monitor)
**Red flag:** Any Grade 5 event; Grade 3+ rate >40% in any cohort

---

### KPI 6 — UAT Pass Rate by Cycle
**Formula:** UAT Scripts Passed ÷ Total UAT Scripts Run × 100, per UAT cycle

**Clinical Relevance:**
User Acceptance Testing (UAT) validates that the EDC system is functioning correctly before data entry begins or after system changes. A low UAT pass rate means the database has configuration errors — forms may not be saving correctly, validation rules may be misfiring, or calculated fields may be wrong. This directly affects data integrity. UAT is a regulatory requirement; the UAT log must be inspection-ready.

**Target:** ≥90% pass rate per cycle
**Red flag:** <80% pass rate in any UAT cycle

---

### KPI 7 — Database Lock Readiness Score
**Formula:** Composite score = (Completeness % × 0.4) + ((1 − Open Query Rate) × 0.4) + (UAT Pass Rate × 0.2)

**Clinical Relevance:**
Database lock is the point at which the database is frozen for statistical analysis. Regulators require the database to be locked before breaking the blind. This composite score gives a single headline metric for lock readiness, used in governance meetings and sponsor updates. A score below 80% means the study is not ready to lock and specific remediation actions are needed.

**Target:** ≥90% for lock to proceed
**Red flag:** <80% — formal remediation plan required

---

### KPI 8 — Enrolment Rate vs Target by Site
**Formula:** Actual Patients Enrolled ÷ Site Target Enrolment × 100

**Clinical Relevance:**
Under-enrolment is the most common reason for Phase I study delays. Sites that are consistently below target may need additional support, protocol amendments, or in extreme cases, replacement. For a Phase I study, insufficient cohort enrolment can leave DLT assessments underpowered, making the safety conclusions unreliable. This KPI is reviewed weekly in study management team meetings.

**Target:** ≥80% of site enrolment target met
**Red flag:** Any site at <60% of target after 6 months

---

## Dashboard Pages Summary

| Page | Purpose | Key Visuals |
|------|---------|-------------|
| **1 — Study Overview** | Executive snapshot | KPI cards, enrolment trend, site table |
| **2 — Query Management** | Query ageing & workload | Ageing bar chart, category donut, site heatmap |
| **3 — Data Quality** | Completeness & safety | Form×visit matrix, SAE status, UAT trend |
| **4 — Lock Readiness** | Lock go/no-go | Readiness gauge, outstanding items, projected lock date |

---

## DAX Measures Reference (Power BI)

```dax
-- Open Query Rate
Open Query Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(queries), queries[status] = "Open"),
    COUNTROWS(data_entry_log),
    0
)

-- Median Resolution Time
Median Resolution Days = 
CALCULATE(
    MEDIANX(queries, queries[age_days]),
    queries[status] = "Resolved"
)

-- Data Entry Completeness
Completeness % = 
DIVIDE(
    CALCULATE(COUNTROWS(data_entry_log), data_entry_log[completed] = TRUE()),
    COUNTROWS(data_entry_log),
    0
)

-- SAE Lag (average)
Avg SAE Lag Days = 
CALCULATE(
    AVERAGE(adverse_events[sae_lag_days]),
    adverse_events[sae_flag] = TRUE()
)

-- Grade 3+ AE Rate
Grade3Plus Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(adverse_events), adverse_events[grade] >= 3),
    COUNTROWS(adverse_events),
    0
)

-- Lock Readiness Score
Lock Readiness Score = 
([Completeness %] * 0.4) + 
((1 - [Open Query Rate]) * 0.4) + 
(CALCULATE(DIVIDE(
    CALCULATE(COUNTROWS(uat_log), uat_log[result]="Pass"),
    COUNTROWS(uat_log),0)) * 0.2)
```

---

## Files in This Repository

```
├── generate_study_data.py          # Python script to regenerate data
├── phase1_oncology_study_data.xlsx # Synthetic dataset (6 sheets)
├── README.md                       # This file
└── dashboard_screenshot.png        # Dashboard preview (add after build)
```

---

## How to Regenerate the Data

```bash
pip install pandas numpy openpyxl
python generate_study_data.py
```

---

*Data is entirely synthetic. No real patient data. Generated for portfolio purposes.*
