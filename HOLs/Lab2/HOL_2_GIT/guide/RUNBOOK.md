# HoL 2 — Demo Walkthrough Guide (YOUR EYES ONLY)

This is your personal demo guide. Walk through it step by step. Attendees don't see this file.

**Account:** https://app.snowflake.com/sfsenorthamerica/lsdemo/
**Context:** SYSADMIN / GSK_GCC_HOL / HOL_2 / COMPUTE_WH

---

## Pre-Flight: Upload to Shared Workspace

Your local files are at `~/.snowflake/cortex/playground/workspace/HOL_2/` (open in Finder — it's a hidden folder).

In Snowsight: **Projects → Workspaces → `gsk_gcc_demos`**

1. Create folder `HOLs/Lab2/`
2. Inside `Lab2/`, create subfolders: `notebooks/` and `fallbacks/`
3. Upload files to match this layout:

```
HOLs/Lab2/
├── attendee-prompt-guide.md
├── slide-deck-outline.md
├── RUNBOOK.md                          ← this file (for your reference)
├── material/
│   ├── GSK_PHARMA_ANALYSIS.ipynb       ← broken notebook (4 intentional errors)
│   ├── GSK_PHARMA_ANALYSIS_FIXED.ipynb ← fully working fallback
│   └── slow-query.sql                  ← Act 6 slow query to paste
└── fallbacks/
    ├── AGENTS.md                       ← Act 4 fallback
    ├── patient_demographics.sql        ← Act 2 fallback
    ├── sis-pharma-dashboard.py         ← Act 5b fallback
    └── drug-insight-report-SKILL.md    ← Act 5a fallback
```

4. **Pre-install the Streamlit skill** (CRITICAL for Act 5a):
   - In the workspace, create folder `.snowflake/cortex/skills/streamlit-dashboard/`
   - Upload `skills/streamlit-dashboard/SKILL.md` into that folder
   - This skill teaches CoCo to use `get_active_session()` instead of `st.connection()` — without it, CoCo generates broken SiS code

5. After uploading, click on each file to verify it opens correctly
6. Click on `GSK_PHARMA_ANALYSIS.ipynb` — it should open as a notebook in the workspace
7. In the notebook, click **Packages** (top-right) → search `matplotlib` → **Add**
   - This pre-installs matplotlib so the Act 3 error is purely the missing `import` line, not a missing package
8. Do the same for `GSK_PHARMA_ANALYSIS_FIXED.ipynb`

**Checkpoint:** You should see all files in the workspace sidebar. Both notebooks should open without errors. The `.snowflake/cortex/skills/streamlit-dashboard/SKILL.md` should exist (verify in sidebar — may be under hidden folders). Don't run anything yet.

---

## Act 1: UI Orientation (5 min)

**Goal:** Show attendees where CoCo lives and how context-awareness works.

### What to do:

1. **Open a SQL file** in the workspace (create a new one or use an existing one)

2. **Open CoCo** — click the Cortex Code icon (bottom-right of Snowsight)

3. **Show context awareness.** Type this into CoCo:
   ```
   What tables exist in GSK_GCC_HOL.HOL_2?
   ```
   **What to expect:** CoCo lists COMPOUNDS, CLINICAL_TRIALS, ADVERSE_EVENTS, SALES_DATA. No PATIENT_DEMOGRAPHICS yet — that's Act 2.

   **Talking point:** "Notice it knows your database structure — schemas, tables, columns. No setup needed."

4. **Demo `@` context references.** Type `@` in the CoCo message box.
   **What to expect:** A dropdown appears showing catalog objects (tables, schemas, views) AND workspace files.
   Pick `GSK_GCC_HOL.HOL_2.COMPOUNDS` — CoCo auto-injects the schema and sample rows as context.

   **Talking point:** "The `@` symbol lets you inject context — tables, files, anything. CoCo sees the schema AND sample data, so it understands your data shape."

5. **Demo CoCo SQL generation.** Ask CoCo:
   ```
   Write a query that shows me the top 5 compounds by number of clinical trials
   ```
   **What to expect:** CoCo generates a complete SQL query with JOINs, GROUP BY, ORDER BY — ready to run.

   **Talking point:** "Plain English in, production SQL out. It knows the schema, the joins, the column names — you just describe what you want."

6. **Explore the data deeper.** Run through a few quick questions to show range:

   ```
   Which therapeutic areas do we have and how many compounds in each?
   ```
   **What to expect:** A grouped summary — shows CoCo can do quick aggregations.

   ```
   Show me the clinical trials that failed and what compounds they were testing
   ```
   **What to expect:** A filtered query joining CLINICAL_TRIALS to COMPOUNDS — shows CoCo understands relationships between tables.

   ```
   Are there any compounds with severe adverse events? Show me the worst offenders.
   ```
   **What to expect:** Joins ADVERSE_EVENTS → CLINICAL_TRIALS → COMPOUNDS, filters on severity. Good pharma-relevant question that gets attendees interested in the data.

   **Talking point:** "We're just having a conversation with our data. No SQL knowledge needed — CoCo figures out the joins and filters."

**Checkpoint:** Attendees understand where CoCo lives, how to open it, and that it knows their Snowflake environment. They've seen it answer real analytical questions.

---

## Act 2: Generate Enrichment Data (10 min)

**Goal:** Show CoCo can generate production-quality DDL + DML from a plain English description.

### What to do:

1. **Paste this prompt into CoCo:**
   ```
   Look at the tables in GSK_GCC_HOL.HOL_2. I need a PATIENT_DEMOGRAPHICS table with 200 rows that links to the CLINICAL_TRIALS table via trial_id. Include patient_id, age, sex, ethnicity, bmi, smoker_status, comorbidities, and enrollment_date.
   ```

2. **Watch CoCo work.** It should:
   - Inspect the CLINICAL_TRIALS table to understand the schema
   - Generate a CREATE TABLE statement with appropriate types
   - Generate INSERT statements with realistic pharma data
   - Link rows to actual trial_id values from CLINICAL_TRIALS

   **Talking point while it generates:** "Notice it's not just making up data — it's looking at your existing tables to understand foreign keys and valid values."

3. **Review the SQL.** CoCo will show you the generated SQL. Look for:
   - Correct column types (INTEGER, VARCHAR, FLOAT, BOOLEAN, DATE)
   - Foreign key relationship to CLINICAL_TRIALS via trial_id
   - Realistic values (ages 18-85, valid ethnicities, BMI ranges)

4. **Run it.** Click Run/Execute on the generated SQL.

5. **Verify with follow-up questions.** Ask CoCo:
   ```
   Show me a summary — row counts for all tables in HOL_2 and a sample of the new PATIENT_DEMOGRAPHICS table.
   ```
   **What to expect:** 5 tables now (COMPOUNDS=50, CLINICAL_TRIALS=30, ADVERSE_EVENTS=100, SALES_DATA=200, PATIENT_DEMOGRAPHICS=~200). Sample rows should look realistic.

6. **Explore the new data.** Ask:
   ```
   What's the age and sex distribution of patients across our clinical trials?
   ```
   **What to expect:** CoCo queries PATIENT_DEMOGRAPHICS, gives a breakdown — proves the generated data is usable for real analysis.

   **Talking point:** "We went from zero to a fully populated, linked table in under a minute. And it's already queryable — real foreign keys, realistic values."

### If CoCo struggles:
Open `fallbacks/patient_demographics.sql` from the workspace, copy the SQL into a SQL file, and run it. Say: "Sometimes with complex generation we might want to refine — let me use a prepared version so we can keep moving."

**Checkpoint:** PATIENT_DEMOGRAPHICS table exists with ~200 rows linked to CLINICAL_TRIALS.

---

## Act 3: Fix the Broken Notebook (10 min)

**Goal:** Show CoCo can diagnose and fix code errors in notebooks — the "Fix with Cortex Code" workflow.

### What to do:

1. **Open the broken notebook.** In the workspace sidebar, click `material/GSK_PHARMA_ANALYSIS.ipynb`.

2. **Confirm matplotlib is added.** Click **Packages** (top-right) — matplotlib should already be listed. If not, add it now.

3. **Run All cells.** Click **Run All** at the top. Every cell will fail.

4. **Walk through each error:**

   **Cell 2 (SQL) — Wrong database name:**
   - Error: `Object 'GSK_GCC_HOLLL' does not exist`
   - The typo is obvious: `GSK_GCC_HOLLL` instead of `GSK_GCC_HOL`
   - Click **"Fix with Cortex Code"** on the error, or ask CoCo: `Fix this SQL — the database name looks wrong`
   - **Expected fix:** `GSK_GCC_HOLLL` → `GSK_GCC_HOL`
   - Run the cell — should succeed

   **Cell 3 (Python) — Wrong column name:**
   - Error: `invalid identifier 'COMPOUND_KEY'`
   - The join uses `compound_key` but the actual column is `compound_id`
   - Ask CoCo: `Fix this — the join column doesn't seem right`
   - **Expected fix:** `compound_key` → `compound_id`
   - Run the cell — should produce a DataFrame with success rates by therapeutic area

   **Cell 4 (Python) — Missing import:**
   - Error: `name 'plt' is not defined`
   - matplotlib is installed (we added the package) but the `import` line is missing
   - Ask CoCo: `Fix this — plt is not defined`
   - **Expected fix:** Adds `import matplotlib.pyplot as plt` at the top of the cell
   - Run the cell — should produce a stacked bar chart of adverse events

   **Cell 5 (Python) — Wrong type conversion:**
   - Error: `invalid literal for int() with base 10: 'Mild'`
   - Code tries `.astype(int)` on the SEVERITY column, but values are strings: Mild, Moderate, Severe
   - Ask CoCo: `Fix this — severity is a string not a number`
   - **Expected fix:** `.astype(int)` → `.map({'Mild': 1, 'Moderate': 2, 'Severe': 3})`
   - Run the cell — should produce a risk score table

5. **Run All again.** All cells should now pass. The stacked bar chart should be visible.

   **Talking point:** "Four different types of bugs — typos, schema mismatches, missing imports, type errors — all fixed in under a minute. No Stack Overflow required."

### If fixes go sideways:
Open `material/GSK_PHARMA_ANALYSIS_FIXED.ipynb` from the workspace instead. Say: "Let me switch to the working version so we can see the expected output."

**Checkpoint:** All cells run successfully. Stacked bar chart visible. Attendees understand the fix workflow.

---

## Act 3b: Build a Notebook from Scratch (5 min)

**Goal:** Show CoCo can build an end-to-end analytics notebook — SQL data prep, Python transformation, chart — in one prompt.

### What to do:

1. **Bridge from Act 3:**
   "You just fixed a broken notebook. Now let's see CoCo build one from scratch — an end-to-end pipeline from raw data to insight, mixing SQL and Python in a single notebook."

2. **Paste this into CoCo:**
   ```
   Build me a notebook called PHARMA_PIPELINE_REPORT that analyses our pharma pipeline. Use COMPUTE_WH and the tables in GSK_GCC_HOL.HOL_2. Start with a SQL cell to set the warehouse, then a SQL cell joining COMPOUNDS (via COMPOUND_NAME = PRODUCT_NAME), CLINICAL_TRIALS and SALES_DATA to summarise by therapeutic area — compound count, trial count, approval rate and total revenue. Then a Python cell to enrich the data with revenue per compound and flag high-confidence areas (>80% approval). Finally a Python cell with an Altair bar chart coloured orange for high confidence and grey for the rest — make sure to enable the mimetype renderer.
   ```

3. **Watch CoCo build it.** It should create a `.ipynb` file with:
   - Cell 1 (SQL): `USE WAREHOUSE COMPUTE_WH`
   - Cell 2 (SQL): JOINs on correct keys, GROUP BY therapeutic area
   - Cell 3 (Python): reads SQL output, adds revenue per compound + high-confidence flag
   - Cell 4 (Python): Altair chart with `alt.renderers.enable('mimetype')` and conditional colour

   **Talking point while it builds:** "Three cells — SQL for the heavy lifting, Python for transformation, Python for visualisation. This is how real analysts work — CoCo just does it faster."

4. **Open the notebook.** Click on it in the workspace sidebar.

5. **Run all cells.** The chart should render showing revenue by therapeutic area with High Confidence areas highlighted in orange.

   **Talking point:** "From zero to a working analytics pipeline in one prompt. SQL, Python, and a chart — all wired together. This is what you'll be building in tomorrow's hackathon."

### If it fails:
- If the notebook doesn't appear, refresh the workspace sidebar
- If cells fail, fix inline with CoCo (demo the fix workflow again — bonus!)
- If still stuck, move on — you've already shown notebook fixing in Act 3

**Checkpoint:** Attendees see CoCo build a multi-cell, multi-language notebook from scratch. They understand the SQL → Python → viz pattern.

---

## Act 4: AGENTS.md — Agent Personality (5 min)

**Goal:** Show how AGENTS.md customises CoCo's behaviour across the entire workspace.

### What to do:

1. **Explain the concept first:**
   "AGENTS.md is a file you drop into your workspace root. CoCo reads it automatically and follows its instructions in every conversation. Think of it as a personality config — you define the rules once, and every team member gets consistent behaviour."

2. **Create it.** Paste this into CoCo:
   ```
   Create an AGENTS.md file for this workspace. The agent should act as a GSK pharmaceutical data analyst, always use GSK_GCC_HOL.HOL_2, give clear non-technical explanations for business stakeholders, add comments to all SQL, and prefer charts over raw tables. Important: the agent must start every response with "🧪 GSK MODE ACTIVATED —" so we can see it's working.
   ```

3. **Watch CoCo create the file.** It should appear in the workspace root (not inside any subfolder).

   **Talking point:** "One file. Every conversation in this workspace now follows these rules. Every analyst on your team gets the same standards."

4. **Test it.** Start a **new CoCo conversation** (important — the old conversation won't pick up the new file). Ask:
   ```
   What are the top 5 compounds by number of clinical trials?
   ```

5. **What to expect:**
   - Response starts with **"🧪 GSK MODE ACTIVATED —"**
   - SQL has comments explaining each step
   - Explanation is business-friendly, not technical jargon
   - May include therapeutic area and phase context
   - Table names are fully qualified (GSK_GCC_HOL.HOL_2.X)

   **Talking point:** "See the 🧪 prefix? That proves AGENTS.md is active. Now look at the SQL — commented, clean. The explanation is written for a business stakeholder, not a DBA. That's the power of AGENTS.md."

6. **Compare (optional, if time allows):** Delete the AGENTS.md, start a new conversation, ask the same question. The response will be more generic/technical. Then restore the file to show the contrast.

### If CoCo doesn't create the file properly:
Copy `fallbacks/AGENTS.md` to the workspace root manually. Start a new conversation and test.

**Checkpoint:** AGENTS.md is in the workspace root. New conversations show "🧪 GSK MODE ACTIVATED —" prefix and follow the persona rules.

---

## Act 5a: Build a Custom Skill (7 min)

**Goal:** Show how to create a reusable skill that anyone in the workspace can invoke.

### What to do:

1. **Ask CoCo about skills.** Type into CoCo:
   ```
   What is a skill in Cortex Code? What skills do I have access to?
   ```
   Let CoCo explain the concept and list the available skills (it should show the pre-installed `streamlit-dashboard` skill plus any built-in ones).

   **Talking point:** "Instead of me explaining it — let's just ask CoCo. It knows what skills are available in this workspace."

2. **Create a new skill.** Paste into CoCo:
   ```
   Create a skill called drug-insight-report. It should take a compound name as input, query COMPOUNDS, CLINICAL_TRIALS, and ADVERSE_EVENTS for that compound from GSK_GCC_HOL.HOL_2, then use Cortex COMPLETE to generate a plain-English executive summary covering: trial status, adverse event profile, and a risk assessment.
   ```

3. **Watch CoCo create the file.** It should create a SKILL.md at `.snowflake/cortex/skills/drug-insight-report/SKILL.md`.

   **Talking point:** "Look at the SKILL.md — it has a name, description, and the SQL template. The description tells CoCo when to use it. The template does the actual work."

4. **Show the skill file.** Click on it in the sidebar. Point out:
   - The frontmatter (name, description, tools)
   - The SQL using Cortex COMPLETE for LLM-powered analysis
   - How it joins across multiple tables for context

5. **Test it.** Ask CoCo:
   ```
   Use the drug-insight-report skill for Rixafolab
   ```

6. **What to expect:** A 4-section executive report covering:
   - Pipeline overview (phase, therapeutic area)
   - Clinical trial status (enrolled patients, success/failure)
   - Adverse event profile (types, severities)
   - Risk assessment and recommendation

   **Talking point:** "That's an AI-generated executive report grounded in your actual data. Not hallucinated — it pulled real trial results, real adverse events. And anyone on your team can run this with one line."

7. **Test with a different compound:**
   ```
   Use the drug-insight-report skill for Dravopimab
   ```
   **Talking point:** "Same skill, different compound. Reusable across your entire pipeline."

### If skill creation fails:
1. In the workspace, create folder `.snowflake/cortex/skills/drug-insight-report/`
2. Copy `fallbacks/drug-insight-report-SKILL.md` into that folder and rename it to `SKILL.md`
3. Test with the same prompts above

**Checkpoint:** Custom skill exists, produces executive reports for any compound. Attendees understand skills = reusable team playbooks.

---

## Act 5b: Generate a GSK-Branded Streamlit App (3 min)

**Goal:** Show how a pre-installed skill produces a polished, branded Streamlit dashboard from a single prompt.

**Background:** The `streamlit-dashboard` skill was pre-installed in `.snowflake/cortex/skills/` during pre-flight. It teaches CoCo the correct SiS patterns (`get_active_session()`, fully qualified tables, `.to_pandas()`) AND enforces GSK branding (orange #F36F21, navy #00205C, logo, styled sidebar). Attendees don't need to know about the pre-install — the point is showing what a well-crafted skill can produce.

### What to do:

1. **Bridge from Act 5a:**
   "You just built a skill from scratch. Now let me show you what a more polished, pre-installed skill can do. We've got a Streamlit skill that knows how to build dashboards with GSK branding — watch this."

2. **Paste this into CoCo:**
   ```
   /streamlit-dashboard Create a GSK pharma pipeline dashboard using GSK_GCC_HOL.HOL_2. Include compound pipeline overview, trial success rates, adverse event breakdown, and revenue by region.
   ```
   > **Note:** The `/streamlit-dashboard` prefix invokes the pre-installed skill. You can also just type the prompt without it — CoCo should auto-match based on trigger words.

3. **Watch CoCo generate the app.** It should create a `.py` file with:
   - GSK logo at the top
   - GSK colour scheme (orange metrics, navy headings, grey background, navy sidebar)
   - `from snowflake.snowpark.context import get_active_session` (NOT `st.connection`)
   - Fully qualified table names (`GSK_GCC_HOL.HOL_2.COMPOUNDS`)
   - `.to_pandas()` calls before passing to Streamlit charts
   - Multiple chart sections (pipeline, trials, AEs, revenue)
   - Clean layout with bordered containers, columns, and metrics

   **Talking point while it generates:** "One prompt, full branded dashboard. The skill handles the connection patterns, the layout, AND your company branding. No boilerplate, no docs hunting."

4. **Show the code.** Scroll through the generated file — point out:
   - The GSK logo and CSS styling at the top
   - The `get_active_session()` connection (SiS-native, no credentials)
   - Fully qualified table references
   - Bordered containers for chart sections

   **Talking point:** "Notice the GSK orange on the metrics, navy headings, the logo — all from the skill. You define your brand standards once in a skill, and every dashboard follows them automatically. That's the power of skills — consistency at scale."

### If generation fails or produces errors:
- If CoCo doesn't apply GSK branding: type `/streamlit-dashboard` explicitly to invoke the skill, then paste the prompt.
- If CoCo generates `st.connection("snowflake")`: the skill didn't activate. Try `/streamlit-dashboard` prefix.
- If still broken: Open `fallbacks/sis-pharma-dashboard.py` and show the code. Say: "Here's what the generated app would look like — complete with GSK branding."

**Checkpoint:** Attendees see a branded GSK Streamlit app generated from a single prompt. They understand skills = consistency + quality at scale.

---

## Act 6: Query History Optimisation (5 min)

**Goal:** Show CoCo can find a slow query in Query History, diagnose performance issues, and rewrite it dramatically faster. This demonstrates Snowsight context awareness beyond just the current file.

### What to do:

1. **Bridge from Act 5b:**
   "We've seen CoCo build things. Now let's see it fix performance problems — using Query History as context."

2. **Open a SQL worksheet.** Create a new SQL file or use an existing one.

3. **Paste the slow query.** Copy the bad query from `material/slow-query.sql` into the SQL worksheet. (This is a deliberately terrible query with CROSS JOINs, recursive CTEs, self-joins, and scalar subqueries — all completely unnecessary.)

   **Talking point while pasting:** "This is a real-world anti-pattern — someone wrote a report query with CROSS JOINs, self-joins, and scalar subqueries. It's functionally correct but horribly inefficient. Let's run it and see."

4. **Run it.** Wait for it to complete — it should take noticeably long for such small tables.

   **Talking point while waiting:** "This is taking ages... on tables with only 50-200 rows each. Imagine this on production data. This is the kind of query that costs you real money."

5. **Go to Query History.** Click into the **Query History** tab in Snowsight. Find the slow query and click into it.

   **Talking point:** "Now I'm going to open CoCo from here — watch how it picks up the query I'm looking at as context."

6. **Open CoCo and ask it to optimise.** Paste into CoCo:
   ```
   This query is way too slow for the data size. What's wrong with it and can you rewrite it to be faster?
   ```

7. **Watch CoCo work.** It should:
   - Find the query in Query History
   - Identify the performance issues (CROSS JOINs, recursive CTE, self-joins, scalar subqueries, unused window functions)
   - Produce an optimised rewrite using CTEs and proper JOINs

   **Talking point:** "CoCo isn't just looking at your current file — it can see your Query History. It found the slow query, diagnosed 9+ performance anti-patterns, and rewrote the whole thing."

8. **Run the optimised query.** Should complete in under 1 second.

   **Talking point:** "From ages to under 1 second. Same results, dramatically faster. And CoCo explained every change it made — recursive CTE removed, CROSS JOINs replaced with proper JOINs, scalar subqueries factored into CTEs."

9. **Compare side by side (optional if time):** Show the query profile for both — the slow one has millions of rows flowing through; the fast one processes a few hundred.

### If it fails:
- If CoCo can't find the query in history, tell it: `The query ID is <paste query ID from results panel>. Optimise it.`
- If the optimised query has errors, ask CoCo to fix them
- If totally stuck, move on to wrap-up — you've already shown the key point

**Checkpoint:** Attendees see CoCo use Query History context, diagnose performance, and produce a dramatically faster rewrite.



**Key messages to land:**
- "CoCo is context-aware everywhere in Snowsight — tables, schemas, files, roles, AND query history"
- "Generate production-quality data with natural language"
- "Fix broken code instantly — one click, no stack trace reading"
- "Build end-to-end notebooks mixing SQL and Python — from data to chart in one prompt"
- "AGENTS.md gives your team consistent standards — one file, every conversation"
- "Skills let you package best practices — build once, use everywhere"
- "CoCo can diagnose and fix slow queries using Query History — dramatically faster rewrites"

**Day 2 hackathon tips:**
- "Start by generating your dummy data — you saw how easy it is"
- "If stuck, just describe what you want in plain English"
- "Use `@` to point CoCo at files, tables, schemas — all in one"
- "Create an AGENTS.md early to set your project context"

---

## Reset for Live Session

After your dry run, clean up so the live demo starts fresh:

### SQL cleanup:
```sql
DROP TABLE IF EXISTS GSK_GCC_HOL.HOL_2.PATIENT_DEMOGRAPHICS;
```

### Workspace cleanup:
- [ ] Delete AGENTS.md from workspace root
- [ ] Delete any Streamlit `.py` files CoCo created
- [ ] Delete any notebook CoCo created (PHARMA_PIPELINE_REPORT)
- [ ] Delete `.snowflake/cortex/skills/drug-insight-report/` folder (the skill CoCo created)
- [ ] If you fixed the broken notebook during dry run, delete it and re-upload the broken `.ipynb` from your local files

### Verify base data:
```sql
SELECT 'COMPOUNDS' AS tbl, COUNT(*) AS cnt FROM GSK_GCC_HOL.HOL_2.COMPOUNDS
UNION ALL SELECT 'CLINICAL_TRIALS', COUNT(*) FROM GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS
UNION ALL SELECT 'ADVERSE_EVENTS', COUNT(*) FROM GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS
UNION ALL SELECT 'SALES_DATA', COUNT(*) FROM GSK_GCC_HOL.HOL_2.SALES_DATA;
```
**Expected:** 50, 30, 100, 200. No PATIENT_DEMOGRAPHICS.

---

## Emergency Fallbacks — Quick Reference

| Problem | Fix |
|---------|-----|
| CoCo doesn't generate PATIENT_DEMOGRAPHICS | Open `fallbacks/patient_demographics.sql`, copy into SQL file, run |
| Notebook fix goes sideways | Open `material/GSK_PHARMA_ANALYSIS_FIXED.ipynb` |
| Notebook build fails (Act 3b) | Fix cells inline with CoCo — doubles as a fix demo. Or skip and move to Act 4 |
| AGENTS.md generation fails | Copy `fallbacks/AGENTS.md` to workspace root, start new conversation |
| Streamlit generation fails | Open `fallbacks/sis-pharma-dashboard.py` and show the code |
| Drug insight skill fails | Copy `fallbacks/drug-insight-report-SKILL.md` to `.snowflake/cortex/skills/drug-insight-report/SKILL.md` |
| Slow query doesn't run long enough | Increase `date_spine` value (WHERE n < 50) in `material/slow-query.sql` |
| CoCo can't find query in history | Give CoCo the query ID from the results panel: `Optimise query <ID>` |
| CoCo is slow / thinking | "While CoCo works on that..." — fill with talking points above |
| Cortex COMPLETE errors | Run `USE WAREHOUSE COMPUTE_WH;` in a SQL file first |
| CoCo unresponsive | Refresh Snowsight, re-open workspace, re-open CoCo panel |
