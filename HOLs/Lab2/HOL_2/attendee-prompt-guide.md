# GSK Cortex Code HoL - Attendee Prompt Guide

All prompts for the presenter to use during the hands-on lab. Copy-paste ready.

---

## Act 1: UI Orientation (5 min)

**Prompt 1 — Context awareness:**
```
What tables exist in TH_DEMO_DB.HOL_2_PHARMA?
```

**Demo: `@` context reference:**
Type `@` in the chat — CoCo shows catalog objects (tables, schemas, views) and workspace files. Pick `TH_DEMO_DB.HOL_2_PHARMA.COMPOUNDS` to auto-inject schema + sample rows.

**Demo: Inline suggestions:**
Start typing in a SQL worksheet: `SELECT * FROM TH_DEMO_DB.HOL_2_PHARMA.` — watch autocomplete appear.

---

## Act 2: Generate Enrichment Data (10 min)

**Prompt 1 — Generate PATIENT_DEMOGRAPHICS:**
```
Look at the tables in TH_DEMO_DB.HOL_2_PHARMA. I need a PATIENT_DEMOGRAPHICS table with 200 rows that links to the CLINICAL_TRIALS table via trial_id. Include patient_id, age, sex, ethnicity, bmi, smoker_status, comorbidities, and enrollment_date.
```

**Prompt 2 — Verify the data:**
```
Show me a summary — row counts for all tables in HOL_2_PHARMA and a sample of the new PATIENT_DEMOGRAPHICS table.
```

**Fallback:** If CoCo struggles, paste `patient_demographics.sql` from the fallbacks folder.

---

## Act 3: Fix the Broken Notebook (10 min)

**Step 1:** Open `GSK_PHARMA_ANALYSIS` notebook from the workspace.

**Step 2:** Run all cells — watch them fail one by one.

**Step 3:** For each failing cell, click "Fix with Cortex Code" or prompt:

**Cell 1 error** (SQL — wrong database name):
```
Fix this SQL — the database name looks wrong
```
*Fix: `TH_DEMO_DBBB` → `TH_DEMO_DB`*

**Cell 2 error** (Python — wrong column name in join):
```
Fix this — the join column doesn't seem right
```
*Fix: `compound_key` → `compound_id`*

**Cell 3 error** (Python — missing matplotlib import):
```
Fix this — plt is not defined
```
*Fix: Add `import matplotlib.pyplot as plt`*

**Cell 4 error** (Python — can't convert string to int):
```
Fix this — severity is a string not a number
```
*Fix: Replace `.astype(int)` with `.map({'Mild': 1, 'Moderate': 2, 'Severe': 3})`*

**Step 4:** Run all cells again — success! Show the chart.

**Fallback:** If fixes go sideways, swap in `GSK_PHARMA_ANALYSIS_FIXED` notebook.

---

## Act 4: AGENTS.md (5 min)

**Prompt — Generate AGENTS.md:**
```
Create an AGENTS.md file for this workspace. The agent should act as a GSK pharmaceutical data analyst, always use TH_DEMO_DB.HOL_2_PHARMA, give clear non-technical explanations for business stakeholders, add comments to all SQL, and prefer charts over raw tables. Important: the agent must start every response with "🧪 GSK MODE ACTIVATED —" so we can see it's working.
```

**Test prompt (to see changed behaviour):**
```
What are the top 5 compounds by number of clinical trials?
```
*Observe: Response starts with "🧪 GSK MODE ACTIVATED —", uses commented SQL, gives business-friendly explanations.*

**Fallback:** Copy `AGENTS.md` from the fallbacks folder into the workspace root.

---

## Act 5a: Generate a Streamlit App (3 min)

**Prompt — Ask CoCo to build a dashboard:**
```
Create a Streamlit in Snowflake app that shows a pharma pipeline dashboard using TH_DEMO_DB.HOL_2_PHARMA. Include compound pipeline overview, trial success rates, adverse event breakdown, and revenue by region.
```

**Talking point while it generates:** "CoCo can generate full Streamlit apps from a single prompt. Next, we'll take it further and build a reusable custom skill."

**Fallback:** Show `sis-pharma-dashboard.py` from fallbacks.

---

## Act 5b: Build Drug Insight Report Skill (7 min)

**Prompt — Create the skill:**
```
Create a skill called drug-insight-report. It should take a compound name as input, query COMPOUNDS, CLINICAL_TRIALS, and ADVERSE_EVENTS for that compound from TH_DEMO_DB.HOL_2_PHARMA, then use Cortex COMPLETE to generate a plain-English executive summary covering: trial status, adverse event profile, and a risk assessment.
```

**Show where the skill file lives:** Point to the SKILL.md in the workspace.

**Test the skill:**
```
Use the drug-insight-report skill for Rixafolab
```

**Second test (different compound):**
```
Use the drug-insight-report skill for Dravopimab
```

**Fallback:** Copy `fallbacks/drug-insight-report-SKILL.md` to `.snowflake/cortex/skills/drug-insight-report/SKILL.md` in the workspace.

---

## Wrap-Up Talking Points

- "CoCo is context-aware everywhere in Snowsight"
- "Generate dummy data with natural language — ready for tomorrow's hackathon"
- "Fix broken code instantly — no stack trace reading"
- "Customise with AGENTS.md — standards for your whole team"
- "Scale best practices with Skills — build once, use everywhere"

**Day 2 hackathon tips:**
- "Start by generating your dummy data — you saw how easy it is"
- "If stuck, describe what you want in plain English"
- "Use `@` to point CoCo at files, tables, schemas — all in one"
- "Create an AGENTS.md early to set your project context"
