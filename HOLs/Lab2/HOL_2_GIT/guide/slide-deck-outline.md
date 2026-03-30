# GSK Cortex Code HoL - Slide Deck Outline

~10 slides, 15 minutes. Presenter-led, no audience interaction until Part 2.

---

## Slide 1: Title
**Lab 2: Cortex Code — Introduction & Basics**
GSK Snowcamp Bangalore | March 2026
Alex Bainbridge, Snowflake

---

## Slide 2: What is Cortex Code?
- AI coding agent native to Snowflake
- Not a chatbot, not a copilot — a full agent
- Understands your entire Snowflake environment: schemas, roles, warehouses, governance
- Works in Snowsight UI, CLI, VS Code, and Desktop

*Visual: Screenshot of CoCo panel in Snowsight*

---

## Slide 3: Where It Works
- **Snowsight:** SQL Worksheets, Notebooks, Streamlit editor
- **CLI:** Terminal, CI/CD pipelines
- **IDE:** VS Code extension, Desktop app
- Context-aware across every surface

*Key point: No other platform does all three (UI + CLI + IDE)*

*Visual: Three-panel showing CoCo in Snowsight, Terminal, and VS Code*

---

## Slide 4: Key Capabilities
- Natural language → SQL / Python
- Inline suggestions & autocomplete
- One-click error fixing
- `@` context referencing (files, tables, schemas, views)
- AGENTS.md — customise agent behaviour per project
- Skills — reusable playbooks (built-in + custom)

---

## Slide 5: Why This Matters — Not All AI Assistants Are Equal
*Frame around capabilities, not naming competitors:*

| Capability | Cortex Code | Others |
|-----------|-------------|--------|
| Full agent with memory | Yes — purpose-built | UI-only assistants given new names |
| Platform awareness | Schemas, roles, RBAC, warehouses, cost, governance | Limited to single catalog/workspace |
| Lifecycle coverage | Ingest → modeling → ML → troubleshoot → deploy | "Write a query" |
| Extensibility | Skills, AGENTS.md, MCP, dbt, Airflow | Locked to own ecosystem |
| Deployment | UI + CLI + IDE | UI only |

---

## Slide 6: Customer Proof Points
- **Braze** (Spencer Burke, SVP Growth): "Engineers spend less time wrestling with context and more time getting precise, actionable outputs."
- **WHOOP** (Matt Luizzi, Sr Dir Analytics): "Accelerated how we turn knowledge into usable AI experiences."
- **Lithia Motors** (Sr SWE Manager): "We've been digging with shovels for years — Snowflake just showed up with dynamite and excavators."
- **Atrium/Slalom**: Rebuilt a Silver layer in dbt — typically a full day, done in 15 minutes.

---

## Slide 7: Interoperability
- Not just Snowflake — CoCo understands your whole stack
- dbt projects, Airflow DAGs
- Migrations from Databricks, Teradata, Oracle, Redshift
- External systems via MCP skills

*Talking point: "If you're multi-cloud or mid-migration, CoCo works with what you have — not just what Snowflake sells."*

---

## Slide 8: Enterprise Roadmap
- Skills managed at enterprise level (on roadmap)
- Create once, share across your org
- Org-wide AGENTS.md standards
- Governance-aware skill distribution

---

## Slide 9: What We'll Build Today
Five acts in 40 minutes:
1. **UI Orientation** — Find CoCo, see context-awareness
2. **Generate Data** — Create an enrichment table with natural language
3. **Fix a Notebook** — Broken pipeline → working pipeline with CoCo Fix
4. **AGENTS.md** — Give CoCo a pharma analyst personality
5. **Skills** — Build a custom skill, then generate a GSK-branded Streamlit app from a pre-installed skill

*Visual: Flow diagram of the 5 acts*

---

## Slide 10: Let's Go
- Open Snowsight
- Navigate to the workspace
- Find the CoCo panel

*Transition to hands-on*
