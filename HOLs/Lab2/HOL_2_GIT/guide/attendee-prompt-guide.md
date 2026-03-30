# GSK Cortex Code HoL - Attendee Prompt Guide

All prompts for the presenter to use during the hands-on lab. Copy-paste ready.

---

## Act 1: UI Orientation (5 min)

**Prompt 1 — Context awareness:**
```
What tables exist in GSK_GCC_HOL.HOL_2?
```

**Demo: `@` context reference:**
Type `@` in the chat — CoCo shows catalog objects (tables, schemas, views) and workspace files. Pick `GSK_GCC_HOL.HOL_2.COMPOUNDS` to auto-inject schema + sample rows.

**Demo: CoCo SQL generation:**
```
Write a query that shows me the top 5 compounds by number of clinical trials
```

**Explore the data — quick-fire questions:**
```
Which therapeutic areas do we have and how many compounds in each?
```
```
Show me the clinical trials that failed and what compounds they were testing
```
```
Are there any compounds with severe adverse events? Show me the worst offenders.
```

---

## Act 2: Generate Enrichment Data (10 min)

**Prompt 1 — Generate PATIENT_DEMOGRAPHICS:**
```
Look at the tables in GSK_GCC_HOL.HOL_2. I need a PATIENT_DEMOGRAPHICS table with 200 rows that links to the CLINICAL_TRIALS table via trial_id. Include patient_id, age, sex, ethnicity, bmi, smoker_status, comorbidities, and enrollment_date.
```

**Prompt 2 — Verify the data:**
```
Show me a summary — row counts for all tables in HOL_2 and a sample of the new PATIENT_DEMOGRAPHICS table.
```

**Prompt 3 — Explore the new data:**
```
What's the age and sex distribution of patients across our clinical trials?
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
*Fix: `GSK_GCC_HOLLL` → `GSK_GCC_HOL`*

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

## Act 3b: Build a Notebook from Scratch (5 min)

**Prompt — Build an end-to-end analytics notebook:**
```
Build me a notebook called PHARMA_PIPELINE_REPORT that analyses our pharma pipeline. Use COMPUTE_WH and the tables in GSK_GCC_HOL.HOL_2. Start with a SQL cell to set the warehouse, then a SQL cell joining COMPOUNDS (via COMPOUND_NAME = PRODUCT_NAME), CLINICAL_TRIALS and SALES_DATA to summarise by therapeutic area — compound count, trial count, approval rate and total revenue. Then a Python cell to enrich the data with revenue per compound and flag high-confidence areas (>80% approval). Finally a Python cell with an Altair bar chart coloured orange for high confidence and grey for the rest — make sure to enable the mimetype renderer.
```

**What to check:** Warehouse set first, SQL joins on correct keys, Python adds computed columns, Altair chart renders with mimetype renderer.



**Prompt — Generate AGENTS.md:**
```
Create an AGENTS.md file for this workspace. The agent should act as a GSK pharmaceutical data analyst, always use GSK_GCC_HOL.HOL_2, give clear non-technical explanations for business stakeholders, add comments to all SQL, and prefer charts over raw tables. Important: the agent must start every response with "🧪 GSK MODE ACTIVATED —" so we can see it's working.
```

**Test prompt (to see changed behaviour):**
```
What are the top 5 compounds by number of clinical trials?
```
*Observe: Response starts with "🧪 GSK MODE ACTIVATED —", uses commented SQL, gives business-friendly explanations.*

**Fallback:** Copy `AGENTS.md` from the fallbacks folder into the workspace root.

---

## Act 5a: Build Drug Insight Report Skill (7 min)

**Explain:** "Skills are reusable playbooks stored as SKILL.md files in `.snowflake/cortex/skills/`. Once created, anyone invokes them with `/` in the CoCo message box."

**Prompt — Create the skill:**
```
Create a skill called drug-insight-report. It should take a compound name as input, query COMPOUNDS, CLINICAL_TRIALS, and ADVERSE_EVENTS for that compound from GSK_GCC_HOL.HOL_2, then use Cortex COMPLETE to generate a plain-English executive summary covering: trial status, adverse event profile, and a risk assessment.
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

## Act 5b: Generate a GSK-Branded Streamlit App (3 min)

**Bridge:** "You just built a skill from scratch. Now watch what a polished, pre-installed skill can do — including GSK branding."

**Prompt — Invoke the Streamlit skill to build a branded dashboard:**
```
/streamlit-dashboard Create a GSK pharma pipeline dashboard using GSK_GCC_HOL.HOL_2. Include compound pipeline overview, trial success rates, adverse event breakdown, and revenue by region.
```
> The `/streamlit-dashboard` prefix invokes the pre-installed skill that ensures correct SiS patterns + GSK branding.

**What to check in generated code:** GSK logo, orange metrics (#F36F21), navy headings (#00205C), `get_active_session()` (NOT `st.connection`), fully qualified table names, `.to_pandas()` before charts.

**Talking point:** "One prompt, branded dashboard. The skill handles connection patterns, layout, AND your company branding. Define standards once, every dashboard follows them."

**Fallback:** Show `sis-pharma-dashboard.py` from fallbacks.

---

## Act 6: Query History Optimisation (5 min)

**Step 1:** Paste the slow query from `material/slow-query.sql` into a SQL worksheet and run it — it should take a while on tiny tables.

**Step 2:** Go to the **Query History** tab in Snowsight. Find the slow query and click into it so CoCo has it as context.

**Prompt — Ask CoCo to optimise it:**
```
This query is way too slow for the data size. What's wrong with it and can you rewrite it to be faster?
```

**What to expect:** CoCo finds the query, identifies 9+ issues (CROSS JOINs, recursive CTE, self-joins, scalar subqueries, unused window functions), rewrites it to run in <1 second.

**Fallback:** If CoCo can't find it, give it the query ID: `Optimise query <paste ID from results panel>`



- "CoCo is context-aware everywhere in Snowsight — tables, schemas, files, AND query history"
- "Generate dummy data with natural language — ready for tomorrow's hackathon"
- "Fix broken code instantly — no stack trace reading"
- "Build end-to-end notebooks mixing SQL and Python in one prompt"
- "Customise with AGENTS.md — standards for your whole team"
- "Scale best practices with Skills — build once, use everywhere"
- "Diagnose and fix slow queries from Query History — dramatically faster rewrites"

**Day 2 hackathon tips:**
- "Start by generating your dummy data — you saw how easy it is"
- "If stuck, describe what you want in plain English"
- "Use `@` to point CoCo at files, tables, schemas — all in one"
- "Create an AGENTS.md early to set your project context"
