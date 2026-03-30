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

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }
    [data-testid="stHeader"] {
        background-color: #00205C;
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
st.title("GSK Pharma Pipeline Dashboard")

try:
    compounds = session.table("GSK_GCC_HOL.HOL_2.COMPOUNDS").to_pandas()
    trials = session.table("GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS").to_pandas()
    adverse = session.table("GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS").to_pandas()
    sales = session.table("GSK_GCC_HOL.HOL_2.SALES_DATA").to_pandas()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

for _df in [compounds, trials, adverse, sales]:
    for col in _df.select_dtypes(include=["object"]).columns:
        _df[col] = pd.to_numeric(_df[col], errors="ignore")

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

col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric("Compounds", f"{len(compounds):,}")
with col2:
    with st.container(border=True):
        st.metric("Clinical Trials", f"{len(trials):,}")
with col3:
    with st.container(border=True):
        st.metric("Adverse Events", f"{len(adverse):,}")
with col4:
    with st.container(border=True):
        st.metric("Approved Drugs", f"{len(compounds[compounds['PHASE'] == 'Approved']):,}")

left, right = st.columns(2)

with left:
    st.subheader("Pipeline by Phase")
    phase_order = ["Discovery", "Preclinical", "Phase I", "Phase II", "Phase III", "Approved"]
    phase_counts = compounds["PHASE"].value_counts().reindex(phase_order, fill_value=0).reset_index()
    phase_counts.columns = ["PHASE", "COUNT"]
    gsk_bar(phase_counts, x="PHASE", y="COUNT", x_title="Phase", y_title="Compounds", sort=None)

with right:
    st.subheader("Trials by Therapeutic Area")
    merged = trials.merge(compounds[["COMPOUND_ID", "THERAPEUTIC_AREA"]], on="COMPOUND_ID")
    ta_counts = merged["THERAPEUTIC_AREA"].value_counts().reset_index()
    ta_counts.columns = ["THERAPEUTIC_AREA", "COUNT"]
    gsk_bar(ta_counts, x="THERAPEUTIC_AREA", y="COUNT", x_title="Area", y_title="Trials", horizontal=True, sort="-x")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Adverse Events by Severity")
    sev_counts = adverse["SEVERITY"].value_counts().reset_index()
    sev_counts.columns = ["SEVERITY", "COUNT"]
    gsk_bar(sev_counts, x="SEVERITY", y="COUNT", x_title="Severity", y_title="Events")

with right2:
    st.subheader("Trial Success Rate")
        completed = trials[trials["STATUS"] == "Completed"]
        if len(completed) > 0:
            success_rate = completed["SUCCESS"].sum() / len(completed) * 100
            st.metric("Overall Success Rate", f"{success_rate:.1f}%")
        active = len(trials[trials["STATUS"] == "Active"])
        st.metric("Active Trials", active)

st.subheader("Revenue by Region")
region_revenue = sales.groupby("REGION")["REVENUE_USD"].sum().sort_values(ascending=False).reset_index()
region_revenue.columns = ["REGION", "REVENUE"]
gsk_bar(region_revenue, x="REGION", y="REVENUE", x_title="Region", y_title="Revenue ($)")

st.subheader("Compound Explorer")

selected = st.selectbox("Select a compound", compounds["COMPOUND_NAME"].sort_values())
comp_row = compounds[compounds["COMPOUND_NAME"] == selected].iloc[0]

c1, c2, c3 = st.columns(3)
c1.write(f"**Therapeutic Area:** {comp_row['THERAPEUTIC_AREA']}")
c2.write(f"**Phase:** {comp_row['PHASE']}")
c3.write(f"**Target:** {comp_row['TARGET_PROTEIN']}")

comp_trials = trials[trials["COMPOUND_ID"] == comp_row["COMPOUND_ID"]]
if len(comp_trials) > 0:
    st.write("**Clinical Trials:**")
    st.dataframe(comp_trials[["TRIAL_ID", "TRIAL_PHASE", "STATUS", "SITE_COUNTRY", "ENROLLED_PATIENTS", "SUCCESS"]], use_container_width=True, hide_index=True)

    trial_ids = comp_trials["TRIAL_ID"].tolist()
    comp_ae = adverse[adverse["TRIAL_ID"].isin(trial_ids)]
    if len(comp_ae) > 0:
        st.write(f"**Adverse Events:** {len(comp_ae)} total")
        st.dataframe(comp_ae[["EVENT_TYPE", "SEVERITY", "OUTCOME", "RELATIONSHIP_TO_DRUG"]], use_container_width=True, hide_index=True)
