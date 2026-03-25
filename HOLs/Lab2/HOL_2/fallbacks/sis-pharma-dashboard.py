import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()
st.set_page_config(page_title="GSK Pharma Dashboard", layout="wide")
st.title("GSK Pharma Pipeline Dashboard")

compounds = session.table("TH_DEMO_DB.HOL_2_PHARMA.COMPOUNDS").to_pandas()
trials = session.table("TH_DEMO_DB.HOL_2_PHARMA.CLINICAL_TRIALS").to_pandas()
adverse = session.table("TH_DEMO_DB.HOL_2_PHARMA.ADVERSE_EVENTS").to_pandas()
sales = session.table("TH_DEMO_DB.HOL_2_PHARMA.SALES_DATA").to_pandas()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Compounds", len(compounds))
col2.metric("Clinical Trials", len(trials))
col3.metric("Adverse Events", len(adverse))
col4.metric("Approved Drugs", len(compounds[compounds["PHASE"] == "Approved"]))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Pipeline by Phase")
    phase_order = ["Discovery", "Preclinical", "Phase I", "Phase II", "Phase III", "Approved"]
    phase_counts = compounds["PHASE"].value_counts().reindex(phase_order, fill_value=0)
    st.bar_chart(phase_counts)

with right:
    st.subheader("Trials by Therapeutic Area")
    merged = trials.merge(compounds[["COMPOUND_ID", "THERAPEUTIC_AREA"]], on="COMPOUND_ID")
    ta_counts = merged["THERAPEUTIC_AREA"].value_counts()
    st.bar_chart(ta_counts)

st.divider()

left2, right2 = st.columns(2)

with left2:
    st.subheader("Adverse Events by Severity")
    sev_counts = adverse["SEVERITY"].value_counts()
    st.bar_chart(sev_counts)

with right2:
    st.subheader("Trial Success Rate")
    completed = trials[trials["STATUS"] == "Completed"]
    if len(completed) > 0:
        success_rate = completed["SUCCESS"].sum() / len(completed) * 100
        st.metric("Overall Success Rate", f"{success_rate:.1f}%")
    active = len(trials[trials["STATUS"] == "Active"])
    st.metric("Active Trials", active)

st.divider()
st.subheader("Revenue by Region")

region_revenue = sales.groupby("REGION")["REVENUE_USD"].sum().sort_values(ascending=False)
st.bar_chart(region_revenue)

st.divider()
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
    st.dataframe(comp_trials[["TRIAL_ID", "TRIAL_PHASE", "STATUS", "SITE_COUNTRY", "ENROLLED_PATIENTS", "SUCCESS"]], use_container_width=True)

    trial_ids = comp_trials["TRIAL_ID"].tolist()
    comp_ae = adverse[adverse["TRIAL_ID"].isin(trial_ids)]
    if len(comp_ae) > 0:
        st.write(f"**Adverse Events:** {len(comp_ae)} total")
        st.dataframe(comp_ae[["EVENT_TYPE", "SEVERITY", "OUTCOME", "RELATIONSHIP_TO_DRUG"]], use_container_width=True)
