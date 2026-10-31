from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from communication.models import AgentStatus
from dashboard.components import (
    CANONICAL_AGENTS,
    analyze_telemetry_dataset,
    build_evidence_table,
    build_findings_table,
    categorize_action,
    diagnose_via_api,
    fetch_report_from_api,
    get_agent_status_grid,
    get_certainty_badge,
    get_confidence_display,
    get_fault_detection_badge,
    get_health_badge,
    list_saved_reports,
    load_saved_report,
    prepare_telemetry_dataframe,
)
from data.csv_loader import load_telemetry_csv
from data.scenarios import (
    SAMPLE_DIR,
    SCENARIO_METADATA,
    generate_scenario_data,
)
from diagnosis.models import DiagnosticReport, NetworkHealthStatus
from orchestrator.orchestrator import CentralOrchestrator

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="NetCoop AI — Multi-Agent NOC",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .noc-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .metric-value-huge {
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .badge-healthy {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-degraded {
        background-color: #78350F;
        color: #FBBF24;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-critical {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-unknown {
        background-color: #334155;
        color: #94A3B8;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .agent-box {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_orchestrator():
    return CentralOrchestrator()


orchestrator = get_orchestrator()

# Initialize session state
if "diagnostic_report" not in st.session_state:
    st.session_state.diagnostic_report = None
if "current_telemetry_df" not in st.session_state:
    records = generate_scenario_data("normal")
    st.session_state.current_telemetry_df = pd.DataFrame(records)
    st.session_state.scenario_name = "normal"

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------

st.sidebar.image("https://img.icons8.com/fluency/96/network-switch.png", width=64)
st.sidebar.title("NetCoop AI")
st.sidebar.caption("Autonomous Multi-Agent Telemetry & Root Cause NOC")
st.sidebar.markdown("---")

input_mode = st.sidebar.radio(
    "Telemetry Input Source",
    options=["Synthetic Scenarios", "CSV File Upload", "Saved Report Lookup"],
    index=0,
)

selected_scenario_id = None
uploaded_file = None

if input_mode == "Synthetic Scenarios":
    scenario_keys = list(SCENARIO_METADATA.keys())
    selected_scenario_id = st.sidebar.selectbox(
        "Select Scenario",
        options=scenario_keys,
        format_func=lambda k: SCENARIO_METADATA[k]["title"],
        index=0,
    )
    meta = SCENARIO_METADATA[selected_scenario_id]
    st.sidebar.info(f"**Expected Outcome:**\n{meta['expected_root_cause']}\n\n_{meta['description']}_")

    if st.sidebar.button("Load Scenario Telemetry", use_container_width=True):
        data = generate_scenario_data(selected_scenario_id)
        st.session_state.current_telemetry_df = pd.DataFrame(data)
        st.session_state.scenario_name = selected_scenario_id
        st.session_state.diagnostic_report = None
        st.sidebar.success(f"Loaded {len(data)} records for {selected_scenario_id}.")

elif input_mode == "CSV File Upload":
    uploaded_file = st.sidebar.file_uploader("Upload Telemetry CSV", type=["csv"])
    if uploaded_file is not None:
        df, warnings = load_telemetry_csv(uploaded_file.getvalue())
        if not df.empty:
            st.session_state.current_telemetry_df = df
            st.session_state.scenario_name = uploaded_file.name
            st.session_state.diagnostic_report = None
            st.sidebar.success(f"Parsed {len(df)} records from CSV.")
            if warnings:
                for w in warnings:
                    st.sidebar.warning(w)
        else:
            st.sidebar.error("Failed to load telemetry from CSV.")

else:  # Saved Report Lookup
    saved_reports = list_saved_reports(orchestrator.reports_dir)

    if saved_reports:
        rep_options = {
            f"{r['report_id']} [{r['health_classification']}] ({r['timestamp'][:19]})": r["report_id"]
            for r in saved_reports
        }
        selected_label = st.sidebar.selectbox("Select Report from History", options=list(rep_options.keys()))
        selected_rep_id = rep_options[selected_label]

        if st.sidebar.button("Load Selected Report", use_container_width=True):
            loaded_rep, err = load_saved_report(selected_rep_id, orchestrator.reports_dir)
            if loaded_rep:
                st.session_state.diagnostic_report = loaded_rep
                st.sidebar.success(f"Loaded Report: {loaded_rep.report_id}")
            else:
                st.sidebar.error(err or "Failed to load report.")
    else:
        st.sidebar.info("No saved reports found in local history directory.")

    st.sidebar.markdown("**— Or Lookup by ID —**")
    direct_id_input = st.sidebar.text_input("Report ID or Diagnosis ID", placeholder="e.g. REP-A1B2C3D4").strip()
    if st.sidebar.button("Fetch Report by ID", use_container_width=True):
        if direct_id_input:
            # 1. Try local repository first
            loaded_rep, err = load_saved_report(direct_id_input, orchestrator.reports_dir)
            if not loaded_rep:
                # 2. Try FastAPI backend if local lookup fails
                loaded_rep, err = fetch_report_from_api(direct_id_input)

            if loaded_rep:
                st.session_state.diagnostic_report = loaded_rep
                st.sidebar.success(f"Retrieved Report: {loaded_rep.report_id}")
            else:
                st.sidebar.error(err or f"Report '{direct_id_input}' could not be retrieved.")
        else:
            st.sidebar.warning("Please enter a valid Report ID or Diagnosis ID.")

st.sidebar.markdown("---")
run_diag_btn = st.sidebar.button("🚀 Run Multi-Agent Diagnosis", type="primary", use_container_width=True)

if run_diag_btn:
    with st.spinner("Dispatching tasks to specialized agents & correlating causal graph..."):
        # First attempt via FastAPI backend
        sc_name = st.session_state.get("scenario_name", "custom")
        api_rep, api_err = diagnose_via_api(
            telemetry=st.session_state.current_telemetry_df,
            scenario_id=sc_name if sc_name in SCENARIO_METADATA else None,
        )
        if api_rep:
            st.session_state.diagnostic_report = api_rep
            st.sidebar.success(f"Diagnosis Complete via API! (ID: {api_rep.report_id})")
        else:
            # Fallback to embedded orchestrator if API is offline
            report = orchestrator.run_diagnosis(
                telemetry=st.session_state.current_telemetry_df,
                scenario_name=sc_name,
                save_report=True,
            )
            st.session_state.diagnostic_report = report
            st.sidebar.success(f"Diagnosis Complete (Local Engine)! (ID: {report.report_id})")

# -----------------------------------------------------------------------------
# HEADER & NETWORK OVERVIEW (SECTION A)
# -----------------------------------------------------------------------------

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("🛰️ NetCoop AI — Multi-Agent Network NOC")
    st.caption("Distributed Specialized Agents • Interoperable JSON Message Bus • Causal Root Cause Analysis")
with col_head2:
    st.markdown(
        f"""
        <div style="text-align: right; padding-top: 15px;">
            <span class="badge-healthy">● ENGINE ONLINE</span><br>
            <small style="color: #94A3B8;">UTC: {datetime.now(timezone.utc).strftime('%H:%M:%S')}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

report: Optional[DiagnosticReport] = st.session_state.diagnostic_report
current_df: pd.DataFrame = st.session_state.current_telemetry_df

# Overview Metric Cards Row 1
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# KPI 1: Overall Network Health
with kpi1:
    st.markdown('<div class="noc-card">', unsafe_allow_html=True)
    health_cls = report.health_classification if report else "UNKNOWN"
    hb = get_health_badge(health_cls)
    st.markdown(f"**Overall Network Health**<br><div class='metric-value-huge' style='color: {hb['color']}; margin-top: 4px;'>{hb['icon']} {hb['label']}</div>", unsafe_allow_html=True)
    st.caption(hb["description"])
    st.markdown('</div>', unsafe_allow_html=True)

# KPI 2: Binary Fault Detection State
with kpi2:
    st.markdown('<div class="noc-card">', unsafe_allow_html=True)
    fault_det = bool(report.fault_detected) if report else False
    fdb = get_fault_detection_badge(fault_det)
    st.markdown(f"**Fault Detection State**<br><div class='metric-value-huge' style='color: {fdb['color']}; margin-top: 4px;'>{fdb['icon']} {fdb['label']}</div>", unsafe_allow_html=True)
    st.caption(fdb["text"])
    st.markdown('</div>', unsafe_allow_html=True)

# KPI 3: Root-Cause Confidence (N/A for healthy networks!)
with kpi3:
    st.markdown('<div class="noc-card">', unsafe_allow_html=True)
    conf_info = get_confidence_display(report)
    conf_color = "#38BDF8" if conf_info["is_applicable"] else "#94A3B8"
    st.markdown(f"**Root-Cause Confidence**<br><div class='metric-value-huge' style='color: {conf_color}; margin-top: 4px;'>{conf_info['display_text']}</div>", unsafe_allow_html=True)
    st.caption(conf_info["subtext"])
    st.markdown('</div>', unsafe_allow_html=True)

# KPI 4: Diagnostic Status & Agent Dispatch
with kpi4:
    st.markdown('<div class="noc-card">', unsafe_allow_html=True)
    diag_status = (report.overall_status or report.execution_status) if report else "AWAITING_RUN"
    succ_count = len(report.successful_agents) if report else 0
    fail_count = len(report.failed_agents) if report else 0
    tout_count = len(report.timed_out_agents) if report else 0

    st.markdown(f"**Diagnosis Status**<br><div style='font-size: 1.3rem; font-weight: 700; color: #F59E0B; margin-top: 6px;'>{diag_status}</div>", unsafe_allow_html=True)
    st.caption(f"Agents: {succ_count} OK • {fail_count} Failed • {tout_count} Timeout")
    st.markdown('</div>', unsafe_allow_html=True)

# Overview Metric Cards Row 2 (Summary Metrics)
sub1, sub2, sub3, sub4 = st.columns(4)
with sub1:
    aff_count = len(report.affected_devices) if report else 0
    st.caption(f"🖥️ **Affected Devices:** {aff_count}")
with sub2:
    findings_count = len(report.validated_findings) if report else 0
    st.caption(f"⚠️ **Active Findings:** {findings_count}")
with sub3:
    recs_count = len(current_df) if not current_df.empty else 0
    st.caption(f"📊 **Evaluated Records:** {recs_count}")
with sub4:
    ts_str = report.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if (report and report.timestamp) else "—"
    st.caption(f"🕒 **Last Diagnosis:** {ts_str}")

# -----------------------------------------------------------------------------
# EXECUTIVE SUMMARY BANNER
# -----------------------------------------------------------------------------

if report:
    certainty_info = get_certainty_badge(report.diagnosis_certainty)
    st.markdown(
        f"""
        <div style="background: #1E293B; border-left: 5px solid {certainty_info['color']}; padding: 14px 18px; border-radius: 8px; margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem;">📋 Unified Diagnostic Executive Summary</span>
                <span>
                    <span style="background: #0F172A; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; color: {certainty_info['color']};">
                        CERTAINTY: {certainty_info['label']}
                    </span>
                    &nbsp;
                    <span style="background: #0F172A; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; color: #94A3B8;">
                        Report: {report.report_id} • Schema v{report.schema_version} ({report.execution_duration_ms or 0:.1f}ms)
                    </span>
                </span>
            </div>
            <p style="margin: 0; color: #CBD5E1; font-size: 0.95rem; line-height: 1.5;">{report.summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if report.warnings or (report.limitations and (report.limitations.missing_telemetry or report.limitations.invalid_records or report.limitations.failed_or_timed_out_agents or report.limitations.stale_observations or report.limitations.notes)):
        with st.expander("⚠️ Diagnostic Limitations, Warnings & Operational Caveats"):
            if report.warnings:
                st.markdown("**Warnings:**")
                for w in report.warnings:
                    st.warning(w)
            if report.limitations:
                if report.limitations.failed_or_timed_out_agents:
                    st.error(f"Missing / Timed-out Domain Agents: {', '.join(report.limitations.failed_or_timed_out_agents)}")
                if report.limitations.stale_observations:
                    st.warning(f"Stale Device Telemetry: {', '.join(report.limitations.stale_observations)}")
                if report.limitations.missing_telemetry:
                    st.info(f"Missing Expected Metrics: {', '.join(report.limitations.missing_telemetry)}")
                if report.limitations.notes:
                    for n in report.limitations.notes:
                        st.caption(f"• {n}")

# -----------------------------------------------------------------------------
# MAIN NOC NAVIGATION TABS
# -----------------------------------------------------------------------------

tab_diag, tab_agents, tab_charts, tab_findings, tab_actions, tab_json = st.tabs([
    "🔍 Diagnostic Summary & Evidence",
    "🤖 Agent Execution Status",
    "📈 Telemetry Visualizations",
    "🔬 Findings & Evidence Explorer",
    "🛠️ Recommendations & Runbooks",
    "📄 Unified JSON Report",
])

# -----------------------------------------------------------------------------
# TAB 1: DIAGNOSTIC SUMMARY & EVIDENCE (SECTION B)
# -----------------------------------------------------------------------------

with tab_diag:
    if report and report.probable_root_cause:
        rc = report.probable_root_cause
        st.subheader("Causal Root-Cause Inference & Synthesis")

        # Distinguish hypothesis from evidence
        st.markdown(
            f"""
            <div style="background: #1E293B; border-left: 5px solid #F59E0B; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="font-size: 0.8rem; font-weight: 700; color: #F59E0B; text-transform: uppercase;">Primary Inferred Root-Cause Hypothesis</span>
                        <h3 style="margin: 4px 0 6px 0; color: #F8FAFC;">{rc.title}</h3>
                    </div>
                    <span style="background: #0F172A; padding: 6px 12px; border-radius: 6px; font-weight: 700; color: #38BDF8;">
                        Confidence: {rc.confidence*100:.1f}%
                    </span>
                </div>
                <p style="margin: 8px 0; color: #CBD5E1; font-size: 1.0rem; line-height: 1.5;">{rc.description}</p>
                <div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #0F172A; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; color: #E2E8F0;">
                        Affected Nodes: {', '.join(rc.affected_devices) if rc.affected_devices else 'Global Scope'}
                    </span>
                    <span style="background: #0F172A; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; color: #F59E0B;">
                        Category: {rc.category}
                    </span>
                    <span style="background: #0F172A; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; color: #10B981;">
                        Certainty: {report.diagnosis_certainty}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### ✅ Corroborating Telemetry Symptoms")
            if rc.supporting_symptoms:
                for sym in rc.supporting_symptoms:
                    st.markdown(f"- **{sym}**")
            else:
                st.write("No corroborating symptoms logged.")

        with col_s2:
            st.markdown("#### ⚠️ Contradicting / Excluded Factors")
            if rc.contradicting_symptoms:
                for sym in rc.contradicting_symptoms:
                    st.markdown(f"- _{sym}_")
            else:
                st.write("No conflicting telemetry observations detected.")

        # Alternative Hypotheses
        alt_causes = report.alternative_causes or report.alternative_hypotheses
        if alt_causes:
            st.markdown("---")
            st.subheader("Competing Hypotheses & Alternative Diagnoses")
            for alt in alt_causes:
                with st.expander(f"Hypothesis: {alt.title} (Confidence: {alt.confidence*100:.1f}%)"):
                    st.write(alt.description)
                    st.markdown(f"**Supporting Factors:** {', '.join(alt.supporting_symptoms) if alt.supporting_symptoms else 'None'}")
                    st.markdown(f"**Contradicting Factors:** {', '.join(alt.contradicting_symptoms) if alt.contradicting_symptoms else 'None'}")

        # Uncertainty Notes
        if report.uncertainty_notes:
            st.markdown("---")
            st.markdown("#### ℹ️ Diagnostic Uncertainty Notes & Evidence Gaps")
            for note in report.uncertainty_notes:
                st.info(f"• {note}")

    else:
        st.info("Click **'🚀 Run Multi-Agent Diagnosis'** in the sidebar to analyze telemetry and generate root cause evidence.")

# -----------------------------------------------------------------------------
# TAB 2: AGENT EXECUTION STATUS (SECTION C)
# -----------------------------------------------------------------------------

with tab_agents:
    st.subheader("Multi-Agent Execution Grid & Health Status")
    st.caption("Inspect execution traces, performance metrics, and error states for each specialized agent.")

    agent_grid = get_agent_status_grid(report)

    for a in agent_grid:
        dur_str = f"{a['duration_ms']:.1f}ms" if a["duration_ms"] is not None else "—"

        st.markdown(
            f"""
            <div class="agent-box" style="border-left: 4px solid {a['status_color']};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">{a['icon']} {a['name']}</span>
                        <div style="font-size: 0.85rem; color: #94A3B8;">{a['domain']}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #1E293B; color: {a['status_color']}; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem;">
                            STATUS: {a['status']}
                        </span>
                        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">Duration: {dur_str}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a1, col_a2 = st.columns([1, 3])
        with col_a1:
            st.metric("Findings", a["findings_count"])
        with col_a2:
            if a["errors"]:
                st.error(f"Errors / Timeouts: {', '.join(a['errors'])}")
            elif a["status"] == "SUCCESS":
                st.caption("Agent executed cleanly with zero exceptions.")

        # Show raw AgentMessage if available
        if report and report.individual_agent_findings and a["agent_id"] in report.individual_agent_findings:
            msg = report.individual_agent_findings[a["agent_id"]]
            with st.expander(f"Inspect {a['name']} JSON Envelope"):
                st.code(msg.model_dump_json(indent=2), language="json")

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: TELEMETRY VISUALIZATIONS (SECTION D)
# -----------------------------------------------------------------------------

with tab_charts:
    st.subheader("Telemetry Analysis & Multi-Dimensional Visualizations")

    clean_df, t_meta = prepare_telemetry_dataframe(current_df)

    if t_meta["is_empty"]:
        st.info("No telemetry records loaded. Please select a scenario, upload a CSV file, or load a saved report.")
    else:
        mode_label = "Chronological Time-Series Mode" if t_meta["mode"] == "time_series" else "Single-Snapshot / Device Comparison Mode"
        st.caption(f"Mode: **{mode_label}** • Total Records: **{t_meta['record_count']}** • Devices: **{t_meta['device_count']}**")

        time_col = "_parsed_ts" if "_parsed_ts" in clean_df.columns else ("timestamp" if "timestamp" in clean_df.columns else clean_df.index)

        # Row 1: Latency & Jitter
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            if "latency_ms" in clean_df.columns and clean_df["latency_ms"].notna().any():
                df_lat = clean_df.dropna(subset=["latency_ms"])
                if t_meta["mode"] == "time_series":
                    fig = px.line(
                        df_lat,
                        x=time_col,
                        y="latency_ms",
                        color="device_id" if "device_id" in df_lat.columns else None,
                        title="Latency (ms) over Time",
                        labels={"latency_ms": "Latency (ms)", time_col: "Timestamp"},
                        template="plotly_dark",
                    )
                else:
                    fig = px.bar(
                        df_lat,
                        x="device_id" if "device_id" in df_lat.columns else df_lat.index,
                        y="latency_ms",
                        title="Round-Trip Transmission Delay (ms) by Device",
                        labels={"latency_ms": "Latency (ms)", "device_id": "Device"},
                        template="plotly_dark",
                        color="latency_ms",
                        color_continuous_scale="Blues",
                    )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        with col_c2:
            if "jitter_ms" in clean_df.columns and clean_df["jitter_ms"].notna().any():
                df_jit = clean_df.dropna(subset=["jitter_ms"])
                if t_meta["mode"] == "time_series":
                    fig = px.line(
                        df_jit,
                        x=time_col,
                        y="jitter_ms",
                        color="device_id" if "device_id" in df_jit.columns else None,
                        title="Jitter Variation (ms) over Time",
                        labels={"jitter_ms": "Jitter (ms)", time_col: "Timestamp"},
                        template="plotly_dark",
                    )
                else:
                    fig = px.bar(
                        df_jit,
                        x="device_id" if "device_id" in df_jit.columns else df_jit.index,
                        y="jitter_ms",
                        title="Delay Variation / Jitter (ms) by Device",
                        labels={"jitter_ms": "Jitter (ms)", "device_id": "Device"},
                        template="plotly_dark",
                        color="jitter_ms",
                        color_continuous_scale="Purples",
                    )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # Row 2: Packet Loss & Bandwidth Utilization
        col_c3, col_c4 = st.columns(2)

        with col_c3:
            if "packet_loss_pct" in clean_df.columns and clean_df["packet_loss_pct"].notna().any():
                df_loss = clean_df.dropna(subset=["packet_loss_pct"])
                if t_meta["mode"] == "time_series":
                    fig = px.line(
                        df_loss,
                        x=time_col,
                        y="packet_loss_pct",
                        color="device_id" if "device_id" in df_loss.columns else None,
                        title="Packet Loss (%) over Time",
                        labels={"packet_loss_pct": "Packet Loss (%)", time_col: "Timestamp"},
                        template="plotly_dark",
                    )
                else:
                    fig = px.bar(
                        df_loss,
                        x="device_id" if "device_id" in df_loss.columns else df_loss.index,
                        y="packet_loss_pct",
                        title="Packet Loss (%) by Device",
                        labels={"packet_loss_pct": "Packet Loss (%)", "device_id": "Device"},
                        template="plotly_dark",
                        color="packet_loss_pct",
                        color_continuous_scale="Reds",
                    )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        with col_c4:
            if "bandwidth_util_pct" in clean_df.columns and clean_df["bandwidth_util_pct"].notna().any():
                df_bw = clean_df.dropna(subset=["bandwidth_util_pct"])
                if t_meta["mode"] == "time_series":
                    fig = px.line(
                        df_bw,
                        x=time_col,
                        y="bandwidth_util_pct",
                        color="device_id" if "device_id" in df_bw.columns else None,
                        title="Link Bandwidth Utilization (%) over Time",
                        labels={"bandwidth_util_pct": "Bandwidth Util (%)", time_col: "Timestamp"},
                        template="plotly_dark",
                    )
                else:
                    fig = px.bar(
                        df_bw,
                        x="device_id" if "device_id" in df_bw.columns else df_bw.index,
                        y="bandwidth_util_pct",
                        title="Interface Bandwidth Utilization (%)",
                        labels={"bandwidth_util_pct": "Bandwidth Util (%)", "device_id": "Device"},
                        template="plotly_dark",
                        color="bandwidth_util_pct",
                        color_continuous_scale="YlOrBr",
                    )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # Row 3: CPU & Memory Utilization
        col_c5, col_c6 = st.columns(2)

        with col_c5:
            if "cpu_util_pct" in clean_df.columns and clean_df["cpu_util_pct"].notna().any():
                df_cpu = clean_df.dropna(subset=["cpu_util_pct"])
                fig = px.bar(
                    df_cpu,
                    x="device_id" if "device_id" in df_cpu.columns else df_cpu.index,
                    y="cpu_util_pct",
                    title="Control Plane CPU Utilization (%)",
                    labels={"cpu_util_pct": "CPU (%)", "device_id": "Device"},
                    template="plotly_dark",
                    color="cpu_util_pct",
                    color_continuous_scale="OrRd",
                )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        with col_c6:
            if "memory_util_pct" in clean_df.columns and clean_df["memory_util_pct"].notna().any():
                df_mem = clean_df.dropna(subset=["memory_util_pct"])
                fig = px.bar(
                    df_mem,
                    x="device_id" if "device_id" in df_mem.columns else df_mem.index,
                    y="memory_util_pct",
                    title="Control Plane Memory Utilization (%)",
                    labels={"memory_util_pct": "RAM (%)", "device_id": "Device"},
                    template="plotly_dark",
                    color="memory_util_pct",
                    color_continuous_scale="Purples",
                )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # Row 4: Throughput & Wi-Fi RSSI
        col_c7, col_c8 = st.columns(2)

        with col_c7:
            if "throughput_mbps" in clean_df.columns and clean_df["throughput_mbps"].notna().any():
                df_tp = clean_df.dropna(subset=["throughput_mbps"])
                fig = px.bar(
                    df_tp,
                    x="device_id" if "device_id" in df_tp.columns else df_tp.index,
                    y="throughput_mbps",
                    title="Observed Network Throughput (Mbps)",
                    labels={"throughput_mbps": "Throughput (Mbps)", "device_id": "Device"},
                    template="plotly_dark",
                    color="throughput_mbps",
                    color_continuous_scale="Teal",
                )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        with col_c8:
            if "wifi_rssi_dbm" in clean_df.columns and clean_df["wifi_rssi_dbm"].notna().any():
                df_wifi = clean_df.dropna(subset=["wifi_rssi_dbm"])
                fig = px.bar(
                    df_wifi,
                    x="device_id",
                    y="wifi_rssi_dbm",
                    title="Wi-Fi Signal Strength (dBm)",
                    labels={"wifi_rssi_dbm": "RSSI (dBm)", "device_id": "Access Point"},
                    template="plotly_dark",
                )
                fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # Row 5: Hardware Queue Drops & Interface CRC Errors (if available)
        hw_cols = [c for c in ["queue_drops", "interface_errors"] if c in clean_df.columns and clean_df[c].notna().any()]
        if hw_cols:
            col_c9, col_c10 = st.columns(2)
            with col_c9:
                if "queue_drops" in hw_cols:
                    df_qd = clean_df.dropna(subset=["queue_drops"])
                    fig = px.bar(
                        df_qd,
                        x="device_id" if "device_id" in df_qd.columns else df_qd.index,
                        y="queue_drops",
                        title="Hardware Queue Drops (count)",
                        labels={"queue_drops": "Queue Drops", "device_id": "Device"},
                        template="plotly_dark",
                    )
                    fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            with col_c10:
                if "interface_errors" in hw_cols:
                    df_ie = clean_df.dropna(subset=["interface_errors"])
                    fig = px.bar(
                        df_ie,
                        x="device_id" if "device_id" in df_ie.columns else df_ie.index,
                        y="interface_errors",
                        title="CRC / Frame Errors (count)",
                        labels={"interface_errors": "CRC Errors", "device_id": "Device"},
                        template="plotly_dark",
                    )
                    fig.update_layout(paper_bgcolor="#1E293B", plot_bgcolor="#0F172A", margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)

        with st.expander("Explore Raw Telemetry Dataframe"):
            st.dataframe(current_df, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: FINDINGS & EVIDENCE EXPLORER (SECTION E)
# -----------------------------------------------------------------------------

with tab_findings:
    st.subheader("Findings & Supporting Evidence Explorer")
    st.caption("Inspect atomic symptom detections from domain agents and corroborating telemetry thresholds.")

    df_findings = build_findings_table(report)

    if not df_findings.empty:
        # Filter controls
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            sev_options = ["ALL"] + sorted(list(df_findings["Severity"].unique()))
            sel_sev = st.selectbox("Filter by Severity", options=sev_options)
        with fcol2:
            agent_options = ["ALL"] + sorted(list(df_findings["Source Agent"].unique()))
            sel_agent = st.selectbox("Filter by Agent", options=agent_options)
        with fcol3:
            dev_options = ["ALL"] + sorted(list(df_findings["Device"].unique()))
            sel_dev = st.selectbox("Filter by Device", options=dev_options)

        # Apply filters
        filtered_df = df_findings
        if sel_sev != "ALL":
            filtered_df = filtered_df[filtered_df["Severity"] == sel_sev]
        if sel_agent != "ALL":
            filtered_df = filtered_df[filtered_df["Source Agent"] == sel_agent]
        if sel_dev != "ALL":
            filtered_df = filtered_df[filtered_df["Device"] == sel_dev]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("No findings logged yet. Execute diagnosis to generate findings.")

    st.markdown("---")
    st.subheader("Consolidated Telemetry Evidence Matrix")

    df_evidence = build_evidence_table(report)
    if not df_evidence.empty:
        st.dataframe(df_evidence, use_container_width=True, hide_index=True)
    else:
        st.info("No supporting evidence breaches recorded.")

# -----------------------------------------------------------------------------
# TAB 5: RECOMMENDATIONS & RUNBOOKS (SECTION F)
# -----------------------------------------------------------------------------

with tab_actions:
    st.subheader("Prescriptive Remediation & Operational Runbooks")

    st.warning("⚠️ **ADVISORY MODE**: NetCoop AI recommendations are purely advisory and require NOC operator confirmation before production execution.")

    if report and (report.recommended_corrective_actions or report.recommendations):
        actions = report.recommended_corrective_actions or report.recommendations
        for act in actions:
            c = categorize_action(act)

            approval_badge = (
                '<span style="background: #450A0A; color: #F87171; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">⚠️ REQUIRES HUMAN APPROVAL</span>'
                if c["requires_human_approval"]
                else '<span style="background: #064E3B; color: #34D399; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">✅ PRE-APPROVED AUTOMATION</span>'
            )

            st.markdown(
                f"""
                <div style="background: #1E293B; border-left: 5px solid {c['priority_color']}; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <span style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">{c['title']}</span>
                            &nbsp;
                            <span style="background: #0F172A; color: {c['category_color']}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">
                                {c['category_label']}
                            </span>
                        </div>
                        <div>
                            <span style="background: #0F172A; color: {c['priority_color']}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">
                                {c['priority_label']}
                            </span>
                            &nbsp;
                            <span style="background: #0F172A; color: {c['risk_color']}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">
                                {c['risk_label']}
                            </span>
                            &nbsp;
                            {approval_badge}
                        </div>
                    </div>
                    <p style="color: #CBD5E1; margin: 8px 0 12px 0; font-size: 0.95rem; line-height: 1.5;">{c['description']}</p>
                    <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;">
                        <strong>Target Devices:</strong> {', '.join(c['affected_devices']) if c['affected_devices'] else 'Network-wide'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Expandable Details (Prerequisites, Verification, Rollback)
            with st.expander(f"Operational Procedures: {c['title']}"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("**Prerequisites:**")
                    if c["prerequisites"]:
                        for p in c["prerequisites"]:
                            st.markdown(f"- {p}")
                    else:
                        st.caption("No special preconditions required.")

                    st.markdown("**Verification Steps:**")
                    if c["verification_steps"]:
                        for v in c["verification_steps"]:
                            st.markdown(f"- {v}")
                    else:
                        st.caption("Verify normal operational metrics after application.")

                with col_r2:
                    st.markdown("**Rollback Instructions:**")
                    if c["rollback_steps"]:
                        for r in c["rollback_steps"]:
                            st.markdown(f"- {r}")
                    else:
                        st.caption("Revert modified parameters to previous baseline configuration.")

                    if c["supporting_evidence"]:
                        st.markdown(f"**Supporting Evidence:** {', '.join(c['supporting_evidence'])}")

            if c["automation_command"]:
                st.markdown("**Automation Command:**")
                st.code(c["automation_command"], language="bash")

            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    else:
        st.info("Run diagnosis to generate actionable runbooks.")

# -----------------------------------------------------------------------------
# TAB 6: UNIFIED JSON REPORT & EXPORT
# -----------------------------------------------------------------------------

with tab_json:
    st.subheader("Unified Diagnostic Report (Schema 2.0.0)")

    if report:
        report_json = report.model_dump_json(indent=2)
        st.download_button(
            label="📥 Download Diagnostic Report (JSON)",
            data=report_json,
            file_name=f"NetCoop-Report-{report.report_id}.json",
            mime="application/json",
            type="primary",
        )
        st.code(report_json, language="json")
    else:
        st.info("No diagnostic report generated yet.")
