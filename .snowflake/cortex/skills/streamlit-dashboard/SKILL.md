---
name: streamlit-dashboard
description: "Create a Streamlit in Snowflake (SiS) dashboard app with GSK branding. Use when: user asks for a streamlit app, dashboard, data visualisation, SiS app, or streamlit dashboard. Triggers: streamlit, dashboard, SiS, visualise, app, chart, metrics."
tools: ["write", "run"]
---

# Streamlit in Snowflake (SiS) Dashboard Builder — GSK Branded

You are building a Streamlit app that runs **inside Snowflake** (Streamlit in Snowflake / SiS).
This is NOT a local Streamlit app. SiS has different APIs, constraints, and patterns. Follow these rules strictly.

## SPEED & SIMPLICITY DIRECTIVE

**Generate the dashboard in ONE pass.** Do not iterate, do not second-guess, do not try alternative approaches.

1. **Write the complete .py file in a single step** — do not write partial code and then edit it
2. **ALWAYS use Altair charts** with GSK orange (`#F36F21`) — do NOT use native `st.bar_chart`/`st.line_chart` (they render in default blue which looks off-brand). Use the helper function pattern from RULE 7.
3. **Deploy using the anonymous stored procedure pattern** in RULE 15 — do NOT try PUT, COPY FILES, or workspace paths (they fail in Snowsight)
4. **Keep the app under 200 lines** — simple is better. 4 KPI metrics, 4-6 charts, 1 detail table is plenty
5. **Do not over-engineer** — no donut/pie charts, no stacked bars, no multi-axis charts. Simple bar + line charts only.

---

## RULE 1: Connection (CRITICAL — most common error)

ALWAYS use this exact pattern. There is no alternative in SiS.

```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
```

NEVER use any of these — they DO NOT WORK in SiS:
- `st.connection("snowflake")` — this is for local Streamlit only
- `snowflake.connector.connect(...)` — this is for local scripts only
- `SnowflakeConnection` — not available in SiS
- `st.secrets` — not used for connection in SiS

---

## RULE 2: Querying Data (CRITICAL — second most common error)

`session.table()` and `session.sql()` return **Snowpark DataFrames**, NOT pandas DataFrames.
You MUST call `.to_pandas()` before passing data to ANY Streamlit display function.

```python
# CORRECT — converts to pandas first
df = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS").to_pandas()
st.dataframe(df)
st.bar_chart(df, x="PHASE", y="COMPOUND_ID")

# WRONG — Snowpark DataFrame cannot be rendered by Streamlit
df = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS")
st.dataframe(df)  # ERROR
```

For SQL queries:
```python
df = session.sql("SELECT PHASE, COUNT(*) AS CNT FROM GSK_GCC_HOL.HOL_2.COMPOUNDS GROUP BY PHASE").to_pandas()
```

ALWAYS fully qualify table names: `DATABASE.SCHEMA.TABLE`

---

## RULE 3: Column Names Are UPPERCASE (CRITICAL — third most common error)

Snowflake returns ALL column names in UPPERCASE. When referencing columns in pandas operations or Streamlit chart parameters, use UPPERCASE.

```python
# CORRECT
st.bar_chart(df, x="PHASE", y="COUNT")
df["THERAPEUTIC_AREA"].value_counts()
df.groupby("REGION")["REVENUE_USD"].sum()

# WRONG — will raise KeyError
st.bar_chart(df, x="phase", y="count")
df["therapeutic_area"].value_counts()
```

---

## RULE 4: Page Config (SiS limitations)

In SiS, `page_title`, `page_icon`, and `menu_items` in `st.set_page_config` are NOT supported and will be silently ignored. Only `layout` works.

```python
# CORRECT for SiS
st.set_page_config(layout="wide")

# These parameters are IGNORED in SiS (no error, but no effect):
# st.set_page_config(page_title="...", page_icon="🧪", layout="wide")
```

---

## RULE 5: Required Imports

```python
import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session
```

Altair is pre-installed in SiS — ALWAYS import it (it is the default charting library for GSK-branded dashboards).
Do NOT import matplotlib, plotly, or other charting libraries unless explicitly requested.

---

## RULE 6: GSK Branding (ALWAYS APPLY)

Every dashboard MUST include GSK branding. Apply immediately after `st.set_page_config()`.

### GSK Brand Colors
- **GSK Orange** (primary accent): `#F36F21`
- **GSK Dark Navy** (headings/text): `#00205C`
- **GSK White** (page background): `#FFFFFF`
- **GSK White**: `#FFFFFF`
- **GSK Green** (positive delta): `#00A651`
- **GSK Red** (negative delta): `#E4002B`

### GSK Logo (inline HTML — no external image dependency)

Do NOT use `st.image()` with external URLs — they often fail in SiS due to network restrictions.
Instead, use inline HTML which is 100% reliable:

```python
st.markdown('<div style="font-size:2.5rem;font-weight:700;color:#F36F21;letter-spacing:0.1em;">GSK</div>', unsafe_allow_html=True)
```

For the sidebar:
```python
with st.sidebar:
    st.markdown('<div style="font-size:1.5rem;font-weight:700;color:#F36F21;letter-spacing:0.1em;">GSK</div>', unsafe_allow_html=True)
```

### Branding Block — include in EVERY app

```python
st.set_page_config(layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #00205C;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    h1, h2, h3 {
        color: #00205C !important;
    }
    [data-testid="stMetricValue"] {
        color: #F36F21 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #00205C !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:2.5rem;font-weight:700;color:#F36F21;letter-spacing:0.1em;">GSK</div>', unsafe_allow_html=True)
```

---

## RULE 7: Charts (CRITICAL — Altair with gradient colour scale)

**ALWAYS use Altair for charts.** Do NOT use native `st.bar_chart` / `st.line_chart` — they render in default Streamlit blue which looks off-brand. Altair is pre-installed in SiS.

Charts MUST use a **gradient colour scale** — bars are coloured from light peach to dark maroon based on their value. This looks professional and polished. A colour legend is shown on the right.

Do NOT wrap charts in `st.container(border=True)` — charts should sit directly on the white page background with just a `st.subheader()` above them.

Define this helper function ONCE near the top of every dashboard (after imports and session setup):

```python
GSK_GRADIENT = alt.Scale(range=["#FDDCBF", "#F36F21", "#C44B0C", "#6B2A06"])

def gsk_bar(df, x, y, x_title=None, y_title=None, height=300, horizontal=False, sort="-y"):
    if horizontal:
        chart = alt.Chart(df).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X(f"{y}:Q", title=y_title or y),
            y=alt.Y(f"{x}:N", title=x_title or x, sort=sort),
            color=alt.Color(f"{y}:Q", scale=GSK_GRADIENT, legend=alt.Legend(title=y_title or y))
        )
    else:
        chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X(f"{x}:N", title=x_title or x, sort=sort, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(f"{y}:Q", title=y_title or y),
            color=alt.Color(f"{y}:Q", scale=GSK_GRADIENT, legend=alt.Legend(title=y_title or y))
        )
    st.altair_chart(chart.properties(height=height).configure_axis(
        gridColor="#E0E0E0", domainColor="#CCCCCC"
    ).configure_view(strokeWidth=0), use_container_width=True)

def gsk_line(df, x, y, x_title=None, y_title=None, height=300):
    chart = alt.Chart(df).mark_line(color="#F36F21", strokeWidth=3, point=alt.OverlayMarkDef(color="#F36F21", size=60)).encode(
        x=alt.X(f"{x}:N", title=x_title or x),
        y=alt.Y(f"{y}:Q", title=y_title or y)
    )
    st.altair_chart(chart.properties(height=height).configure_axis(
        gridColor="#E0E0E0", domainColor="#CCCCCC"
    ).configure_view(strokeWidth=0), use_container_width=True)
```

Then use them like this — note NO `st.container(border=True)` wrapper:
```python
left, right = st.columns(2)
with left:
    st.subheader("Pipeline by Phase")
    gsk_bar(phase_counts, x="PHASE", y="COUNT", x_title="Phase", y_title="Compounds")
with right:
    st.subheader("Trials by Area")
    gsk_bar(ta_counts, x="THERAPEUTIC_AREA", y="COUNT", horizontal=True, sort="-x", y_title="Trials")
```

**Chart rules:**
- ALWAYS use `gsk_bar()` or `gsk_line()` — never raw `st.bar_chart` or `st.line_chart`
- ALWAYS use gradient colour scale (`GSK_GRADIENT`) — never flat single-colour bars
- Do NOT wrap charts in `st.container(border=True)` — let them sit on white background
- NEVER use donut/pie charts, stacked bars, or multi-axis charts
- Use `horizontal=True` for category charts with long labels (e.g. therapeutic areas, countries)
- Use `sort="-y"` (descending by value) or `sort="-x"` for horizontal charts
- Use `None` for sort when x-axis has a natural order (e.g. phases: Preclinical → Approved)
- The colour legend appears automatically on the right — this is intentional and looks good

---

## RULE 8: Layout Patterns

### KPI Row (wrap each metric in a bordered container)
```python
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric("Compounds", f"{len(compounds):,}")
with col2:
    with st.container(border=True):
        st.metric("Trials", f"{len(trials):,}")
with col3:
    with st.container(border=True):
        st.metric("Adverse Events", f"{len(adverse):,}")
with col4:
    with st.container(border=True):
        st.metric("Approved", f"{approved_count:,}")
```

NEVER use `st.metric(..., border=True)` — this parameter does NOT exist in the SiS Streamlit version.

### Two-Column Charts (NO border wrapper — charts sit on white background)
```python
left, right = st.columns(2)
with left:
    st.subheader("Chart Title")
    gsk_bar(data, x="CATEGORY", y="VALUE")
with right:
    st.subheader("Chart Title")
    gsk_line(data, x="DATE", y="AMOUNT")
```

### Sidebar Filters (will be navy with white text from GSK CSS)
```python
with st.sidebar:
    st.markdown('<div style="font-size:1.5rem;font-weight:700;color:#F36F21;letter-spacing:0.1em;">GSK</div>', unsafe_allow_html=True)
    st.markdown("---")
    selected = st.selectbox("Filter", options)
```

### Data Tables
```python
st.dataframe(df, use_container_width=True, hide_index=True)
```

---

## RULE 9: Code Structure (CRITICAL — CoCo often gets this wrong)

Streamlit reruns the ENTIRE script on every widget interaction. Do NOT wrap code in a main function or class.

```python
# CORRECT — sequential script, no wrapper
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()
st.set_page_config(layout="wide")
df = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS").to_pandas()
st.dataframe(df)

# WRONG — will not work correctly in Streamlit
def main():
    st.title("Dashboard")
    ...

if __name__ == "__main__":
    main()
```

---

## RULE 10: SiS API Version Constraints (CRITICAL)

The SiS warehouse runtime runs an OLDER Streamlit version. Many newer Streamlit APIs do NOT work.

**DO NOT USE these — they will crash the app:**
- `st.metric(..., border=True)` — use `st.container(border=True)` wrapper instead
- `st.metric(..., chart_data=...)` — sparklines not available
- `st.logo()` — not available
- `st.badge()` — not available
- `st.space()` — not available
- `st.pills()` — not available
- `st.segmented_control()` — not available
- `st.container(horizontal=True)` — not available
- `st.image()` with external URLs — often fails due to network restrictions

**SAFE to use (confirmed working in SiS):**
- `st.container(border=True)` — for bordered cards
- `st.columns()` — for layout
- `st.metric()` — without border param
- `st.bar_chart()`, `st.line_chart()`, `st.area_chart()` — native charts
- `st.altair_chart()` — Altair is pre-installed
- `st.selectbox()`, `st.multiselect()`, `st.slider()` — standard widgets
- `st.markdown(..., unsafe_allow_html=True)` — for CSS and HTML branding
- `st.dataframe(hide_index=True)` — with column_config

---

## RULE 11: Error Handling

Wrap data loading in try/except so the app shows a helpful message instead of a raw traceback:

```python
try:
    session = get_active_session()
    compounds = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS").to_pandas()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()
```

---

## RULE 12: Number Formatting on Metrics

Format metric values for readability. Never display raw integers or floats.

```python
# CORRECT
col1.metric("Total Revenue", f"${revenue:,.0f}")
col2.metric("Compounds", f"{len(compounds):,}")
col3.metric("Approval Rate", f"{rate:.1f}%")

# WRONG — raw unformatted numbers
col1.metric("Total Revenue", revenue)
col2.metric("Compounds", len(compounds))
```

---

## RULE 13: Dataframe Formatting

Use `column_config` to format currencies, percentages, and dates in dataframes:

```python
st.dataframe(
    df,
    column_config={
        "REVENUE_USD": st.column_config.NumberColumn("Revenue", format="$%.2f"),
        "APPROVAL_RATE": st.column_config.ProgressColumn("Approval", min_value=0, max_value=100),
        "START_DATE": st.column_config.DateColumn("Start Date", format="MMM DD, YYYY"),
        "INTERNAL_ID": None,  # hides column from display
    },
    use_container_width=True,
    hide_index=True,
)
```

---

## RULE 14: Numeric Type Casting (CRITICAL — common with arithmetic)

Snowflake `NUMBER` columns arrive as Python `Decimal` type after `.to_pandas()`, stored as `object` dtype.
Arithmetic on these columns will fail with `TypeError: Expected numeric dtype, got object instead.`

ALWAYS cast numeric columns before doing math:

```python
# CORRECT — cast to numeric before arithmetic
df["ENROLLED_PATIENTS"] = pd.to_numeric(df["ENROLLED_PATIENTS"])
df["REVENUE_USD"] = pd.to_numeric(df["REVENUE_USD"])
rate = (df["SUCCESSES"].astype(float) / df["TOTAL"].astype(float) * 100).round(1)

# SHORTCUT — cast all numeric-like columns at once after .to_pandas()
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = pd.to_numeric(df[col], errors="ignore")

# WRONG — will crash on Decimal/object columns
rate = df["SUCCESSES"] / df["TOTAL"] * 100  # TypeError!
```

---

## Common Errors to AVOID

| Error | Cause | Fix |
|-------|-------|-----|
| `SnowflakeConnection not found` | Using `st.connection("snowflake")` | Use `get_active_session()` |
| `KeyError: 'phase'` | Lowercase column name | Use UPPERCASE: `"PHASE"` |
| `cannot display Snowpark DataFrame` | Missing `.to_pandas()` | Add `.to_pandas()` after every query |
| `No module named 'snowflake.connector'` | Wrong import | Use `from snowflake.snowpark.context import get_active_session` |
| Page title/icon not showing | SiS limitation | Only `layout` param works in `st.set_page_config` |
| `if __name__ == "__main__":` | Wrong code structure | Remove it — Streamlit runs the whole file on every interaction |
| Raw traceback on screen | No error handling | Wrap data loading in `try/except` with `st.error()` + `st.stop()` |
| `unexpected keyword argument 'border'` on metric | `st.metric(border=True)` not in SiS version | Wrap metric in `st.container(border=True)` instead |
| Broken image / `:0` | `st.image()` with external URL fails in SiS | Use inline HTML: `st.markdown('<div style="...">GSK</div>', unsafe_allow_html=True)` |
| `Expected numeric dtype, got object` | Snowflake NUMBER → Python Decimal → pandas object | Cast first: `pd.to_numeric(df["COL"])` or `.astype(float)` |

---

## RULE 15: Auto-Deployment (CRITICAL — always deploy after writing)

After writing the .py file, you MUST deploy it as a Streamlit in Snowflake app. Do NOT tell the user to deploy manually.

**IMPORTANT: `PUT` does NOT work from Snowsight SQL worksheets.** Use an anonymous stored procedure to upload the file content to a stage, then create the Streamlit object.

Follow these steps IN ORDER:

1. **Write the .py file** to the workspace (you already do this).
2. **Create a stage** (if it doesn't already exist):
   ```sql
   CREATE STAGE IF NOT EXISTS HOL_2_WORK.HOL_2.STREAMLIT_STAGE
       DIRECTORY = (ENABLE = TRUE)
       ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
   ```
3. **Upload the file content** using an anonymous Python stored procedure (this works in Snowsight):
   ```sql
   WITH upload_dashboard AS PROCEDURE()
       RETURNS STRING
       LANGUAGE PYTHON
       RUNTIME_VERSION = '3.9'
       PACKAGES = ('snowflake-snowpark-python')
       HANDLER = 'run'
   AS $$
   def run(session):
       import io
       code = '''<PASTE THE ENTIRE .py FILE CONTENT HERE>'''
       session.file.put_stream(
           io.BytesIO(code.encode('utf-8')),
           '@HOL_2_WORK.HOL_2.STREAMLIT_STAGE/dashboard.py',
           auto_compress=False, overwrite=True
       )
       return 'uploaded'
   $$
   CALL upload_dashboard();
   ```
   Replace `<PASTE THE ENTIRE .py FILE CONTENT HERE>` with the actual dashboard code. Use triple-quoted strings (`'''...'''`) and escape any internal triple-quotes.
4. **Create the Streamlit app object:**
   ```sql
   CREATE OR REPLACE STREAMLIT HOL_2_WORK.HOL_2.GSK_DASHBOARD
       ROOT_LOCATION = '@HOL_2_WORK.HOL_2.STREAMLIT_STAGE'
       MAIN_FILE = 'dashboard.py'
       QUERY_WAREHOUSE = 'COMPUTE_WH';
   ```
5. **Tell the user** the app is deployed and they can open it in Snowsight.

Adjust database, schema, stage name, app name, file name, and warehouse to match the user's context.
If the user's warehouse or database is unknown, ask — but always deploy.

---

## Full Template

Every new dashboard should follow this exact structure:

```python
import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

try:
    session = get_active_session()
except Exception as e:
    st.error(f"Failed to connect: {e}")
    st.stop()

st.set_page_config(layout="wide")

GSK_GRADIENT = alt.Scale(range=["#FDDCBF", "#F36F21", "#C44B0C", "#6B2A06"])

def gsk_bar(df, x, y, x_title=None, y_title=None, height=300, horizontal=False, sort="-y"):
    if horizontal:
        chart = alt.Chart(df).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X(f"{y}:Q", title=y_title or y),
            y=alt.Y(f"{x}:N", title=x_title or x, sort=sort),
            color=alt.Color(f"{y}:Q", scale=GSK_GRADIENT, legend=alt.Legend(title=y_title or y))
        )
    else:
        chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X(f"{x}:N", title=x_title or x, sort=sort, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(f"{y}:Q", title=y_title or y),
            color=alt.Color(f"{y}:Q", scale=GSK_GRADIENT, legend=alt.Legend(title=y_title or y))
        )
    st.altair_chart(chart.properties(height=height).configure_axis(
        gridColor="#E0E0E0", domainColor="#CCCCCC"
    ).configure_view(strokeWidth=0), use_container_width=True)

def gsk_line(df, x, y, x_title=None, y_title=None, height=300):
    chart = alt.Chart(df).mark_line(color="#F36F21", strokeWidth=3, point=alt.OverlayMarkDef(color="#F36F21", size=60)).encode(
        x=alt.X(f"{x}:N", title=x_title or x),
        y=alt.Y(f"{y}:Q", title=y_title or y)
    )
    st.altair_chart(chart.properties(height=height).configure_axis(
        gridColor="#E0E0E0", domainColor="#CCCCCC"
    ).configure_view(strokeWidth=0), use_container_width=True)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #00205C; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3 { color: #00205C !important; }
    [data-testid="stMetricValue"] { color: #F36F21 !important; }
    [data-testid="stMetricLabel"] { color: #00205C !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:2.5rem;font-weight:700;color:#F36F21;letter-spacing:0.1em;">GSK</div>', unsafe_allow_html=True)
st.title("Dashboard Title")

try:
    compounds = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS").to_pandas()
    trials = session.table("GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS").to_pandas()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

for _df in [compounds, trials]:
    for col in _df.select_dtypes(include=["object"]).columns:
        _df[col] = pd.to_numeric(_df[col], errors="ignore")

col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric("Compounds", f"{len(compounds):,}")
with col2:
    with st.container(border=True):
        st.metric("Trials", f"{len(trials):,}")
with col3:
    with st.container(border=True):
        st.metric("Metric 3", f"{value3:,}")
with col4:
    with st.container(border=True):
        st.metric("Metric 4", f"{value4:,}")

left, right = st.columns(2)
with left:
    st.subheader("Chart 1")
    gsk_bar(compounds, x="COLUMN_A", y="COLUMN_B")
with right:
    st.subheader("Chart 2")
    gsk_line(trials, x="COLUMN_X", y="COLUMN_Y")

st.subheader("Details")
st.dataframe(
    compounds,
    column_config={
        "REVENUE_USD": st.column_config.NumberColumn("Revenue", format="$%.2f"),
    },
    use_container_width=True,
    hide_index=True,
)
```
