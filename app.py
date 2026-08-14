"""Interactive GRC Compliance Gap Analysis Dashboard."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.assessment import (
    AssessmentConfig,
    calculate_assessment,
    overall_metrics,
    summarize_by,
    top_priorities,
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "fictional_company_controls.csv"

st.set_page_config(
    page_title="Compliance Gap Analysis Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #071216; }
    .block-container { max-width: 1440px; padding-top: 2.2rem; }
    .hero { padding: 1.4rem 1.6rem; border: 1px solid #24454a; border-radius: 18px;
            background: linear-gradient(120deg, #102b30 0%, #071216 65%); margin-bottom: 1rem; }
    .hero h1 { margin: 0; font-size: 2.35rem; color: #f4efe3; }
    .hero p { color: #adc5c3; margin: .55rem 0 0; font-size: 1.02rem; }
    .section-label { color: #e3b75b; text-transform: uppercase; letter-spacing: .12em;
                     font-size: .75rem; font-weight: 700; margin-top: 1.25rem; }
    .notice { border-left: 4px solid #e3b75b; padding: .8rem 1rem; background: #102126;
              color: #c9d8d5; border-radius: 4px; }
    [data-testid="stMetricValue"] { color: #f4efe3; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE, keep_default_na=False)


def as_csv(data: pd.DataFrame) -> bytes:
    return data.to_csv(index=False).encode("utf-8")


st.markdown(
    """
    <div class="hero">
      <div class="section-label">GRC / CONTROL ASSURANCE</div>
      <h1>Compliance Gap Analysis Dashboard</h1>
      <p>Evidence-aware posture analysis for a fictional organization — built on NIST CSF 2.0 outcomes.</p>
    </div>
    <div class="notice"><strong>Portfolio demonstration:</strong> the organization, assessments, and findings are fictional. This tool supports prioritization; it is not an audit opinion or a certification assessment.</div>
    """,
    unsafe_allow_html=True,
)

raw = load_data()
with st.sidebar:
    st.markdown("### Assessment lens")
    st.caption("Change filters to explore the control environment.")
    framework = st.multiselect("Framework", sorted(raw["framework"].unique()), default=sorted(raw["framework"].unique()))
    functions = st.multiselect("NIST Function", sorted(raw["function"].unique()), default=sorted(raw["function"].unique()))
    owners = st.multiselect("Owner", sorted(raw["owner"].unique()), default=sorted(raw["owner"].unique()))
    st.divider()
    status_weight = st.slider("Status score weight", 0.0, 1.0, 0.70, 0.05)
    st.caption("Evidence weight is the remainder. Scores are transparent and illustrative.")
    st.divider()
    st.markdown("### About the method")
    st.write("Maturity = 70% implementation status + 30% evidence strength. Gap and risk are calculated per control and shown with the assumptions visible.")

filtered = raw[
    raw["framework"].isin(framework)
    & raw["function"].isin(functions)
    & raw["owner"].isin(owners)
].copy()

if filtered.empty:
    st.warning("No controls match the selected filters. Select at least one value in each filter.")
    st.stop()

assessment = calculate_assessment(filtered, AssessmentConfig(status_weight=status_weight, evidence_weight=1 - status_weight))
metrics = overall_metrics(assessment)

st.markdown('<div class="section-label">Executive view</div>', unsafe_allow_html=True)
metric_cols = st.columns(5)
metric_cols[0].metric("Controls in view", metrics["controls"])
metric_cols[1].metric("Average maturity", f"{metrics['maturity_percent']}%")
metric_cols[2].metric("Average gap", f"{metrics['gap_percent']}%")
metric_cols[3].metric("High / critical", metrics["high_risk"])
metric_cols[4].metric("Documented evidence", f"{metrics['documented_evidence']}%")

left, right = st.columns([1.25, 1])
with left:
    st.markdown('<div class="section-label">Posture by NIST function</div>', unsafe_allow_html=True)
    by_function = summarize_by(assessment, "function")
    fig = px.bar(
        by_function.sort_values("maturity_percent"),
        x="maturity_percent",
        y="function",
        orientation="h",
        text="maturity_percent",
        labels={"maturity_percent": "Maturity %", "function": "Function"},
        color="maturity_percent",
        color_continuous_scale=["#b54f49", "#e3b75b", "#5eaaa0"],
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, margin=dict(l=0, r=20, t=20, b=10), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-label">Risk distribution</div>', unsafe_allow_html=True)
    risk_order = ["Critical", "High", "Moderate", "Low"]
    risk_counts = assessment["risk_band"].value_counts().reindex(risk_order, fill_value=0).reset_index()
    risk_counts.columns = ["risk_band", "controls"]
    fig = px.pie(risk_counts, names="risk_band", values="controls", hole=.62, color="risk_band", color_discrete_map={"Critical": "#b54f49", "High": "#d8844d", "Moderate": "#e3b75b", "Low": "#5eaaa0"})
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)", legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-label">Action register</div>', unsafe_allow_html=True)
st.caption("Sorted by transparent risk score: gap percentage × priority weight × 25.")
priority_view = top_priorities(assessment, 12)
st.dataframe(priority_view, use_container_width=True, hide_index=True, column_config={
    "risk_score": st.column_config.NumberColumn("Risk score", format="%.1f"),
    "gap_percent": st.column_config.NumberColumn("Gap", format="%.1f%%"),
})

with st.expander("Explore all assessed controls", expanded=False):
    st.dataframe(assessment, use_container_width=True, hide_index=True)

st.markdown('<div class="section-label">Export and methodology</div>', unsafe_allow_html=True)
export_left, export_right = st.columns(2)
with export_left:
    st.download_button("Download action register (CSV)", as_csv(priority_view), "grc_action_register.csv", "text/csv", use_container_width=True)
with export_right:
    report = {
        "assessment_name": "Fictional organization — NIST CSF 2.0 portfolio demonstration",
        "method": {"status_weight": status_weight, "evidence_weight": 1 - status_weight},
        "metrics": metrics,
        "controls": assessment.to_dict(orient="records"),
    }
    st.download_button("Download assessment report (JSON)", json.dumps(report, indent=2), "grc_assessment_report.json", "application/json", use_container_width=True)

st.caption("Framework basis: NIST Cybersecurity Framework 2.0. ISO/IEC 27001:2022 references are included as indicative crosswalk labels only; the full standard text is not reproduced.")
