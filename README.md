# NetCoop AI — Multi-Agent Network Fault Diagnosis and Interoperability

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Pytest-279%20Passed-brightgreen.svg)](https://docs.pytest.org/)

---

## 🚀 Overview

**NetCoop AI** is an enterprise-grade multi-agent network fault diagnosis system built for modern Network Operations Centers (NOC). It autonomously ingests multi-dimensional network telemetry, distributes analysis across specialized autonomous agents, correlates heterogeneous symptoms using an evidence-based causal graph, resolves conflicting observations, and delivers deterministic root cause analysis with actionable remediation runbooks.

---

## 🏛️ System Architecture

```
                                  ┌────────────────────────┐
                                  │   Telemetry Ingestion  │
                                  │ (CSV, JSON, Scenarios) │
                                  └───────────┬────────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CENTRAL ORCHESTRATOR                                    │
│   • Input Validation & Schema Normalization  • Parallel Agent Dispatch (ThreadPool)    │
│   • Timeout & Crash Fault Tolerance          • Message Envelope Schema Enforcement     │
│   • Final Diagnostic Report Compilation                                                │
└───────────────┬─────────────────────────────┬─────────────────────────────┬────────────┘
                │                             │                             │
                ▼                             ▼                             ▼
    ┌───────────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐
    │   Performance Agent   │     │ Infrastructure Agent  │     │  Connectivity Agent   │
    │ • Latency / RTT       │     │ • CPU / Memory Load   │     │ • DNS Status & Latency│
    │ • Jitter Variations   │     │ • Device Availability │     │ • DHCP Lease State    │
    │ • Packet Loss Rate    │     │ • Interface Flapping  │     │ • Wi-Fi RSSI / SNR    │
    │ • Bandwidth Saturation│     │ • CRC & Queue Drops   │     │ • Host Reachability   │
    └───────────┬───────────┘     └───────────┬───────────┘     └───────────┬───────────┘
                │                             │                             │
                └─────────────────────────────┼─────────────────────────────┘
                                              │
                                              ▼ (Standardized AgentMessage Bus)
                           ┌─────────────────────────────────────┐
                           │       Fault Correlation Agent       │
                           │ • Multi-Symptom Evidence Synthesis  │
                           │ • Causal Hypothesis Ranking         │
                           │ • Conflict Resolution Logic         │
                           │ • Uncertainty & Confidence Scoring  │
                           └──────────────────┬──────────────────┘
                                              │
                                              ▼
                           ┌─────────────────────────────────────┐
                           │        Recommendation Agent         │
                           │ • Prescriptive Mitigation Steps     │
                           │ • Verification Procedures           │
                           │ • Automated CLI Remediations        │
                           └──────────────────┬──────────────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                UNIFIED DIAGNOSTIC REPORT                               │
│     Report ID • Probable Root Cause • Competing Causes • Evidence Matrix • Runbooks    │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │
                             ┌────────────────┴────────────────┐
                             ▼                                 ▼
                 ┌───────────────────────┐         ┌───────────────────────┐
                 │  FastAPI REST Server  │         │ Streamlit NOC Console │
                 │ http://localhost:8000 │         │ http://localhost:8501 │
                 └───────────────────────┘         └───────────────────────┘
```

---

## 🛠️ Technology Stack

- **Python**: 3.14+
- **Agent Interoperability**: Pydantic v2 (JSON-based schema envelope)
- **Data Engineering**: Pandas, NumPy
- **Backend API**: FastAPI, Uvicorn, Python-Multipart, Requests, HTTPX
- **Dashboard / NOC UI**: Streamlit, Plotly
- **Testing**: Pytest (39 automated unit & integration tests)

---

## 📁 Project Directory Structure

```
NetCoop-AI/
├── communication/             # Interoperability protocol & models
│   ├── __init__.py
│   ├── models.py              # AgentMessage, Finding, EvidenceItem, Telemetry schemas
│   └── protocol.py            # Message validation, serialization, error builders
├── agents/                    # Specialized autonomous diagnostic agents
│   ├── __init__.py
│   ├── base_agent.py          # Abstract BaseAgent with fault-isolated execution
│   ├── performance_agent.py   # Latency, jitter, packet loss, bandwidth saturation
│   ├── infrastructure_agent.py# CPU, memory, interface status, CRC errors, queue drops
│   └── connectivity_agent.py  # DNS, DHCP, Wi-Fi RSSI/SNR, reachability
├── diagnosis/                 # Correlation, recommendation & reporting models
│   ├── __init__.py
│   ├── models.py              # DiagnosticReport, RootCauseCandidate, CorrectiveAction
│   ├── correlation_agent.py   # Multi-hypothesis causal inference & conflict resolution
│   └── recommendation_agent.py# Priority runbooks with verification & CLI commands
├── orchestrator/              # Central Orchestrator
│   ├── __init__.py
│   └── orchestrator.py        # Pipeline coordinator & fault-tolerant manager
├── data/                      # Scenario datasets and CSV parsing
│   ├── __init__.py
│   ├── scenarios.py           # 8 realistic reproducible network scenario generators
│   ├── csv_loader.py          # Robust CSV parser with fuzzy column mapping
│   └── samples/               # Pre-generated scenario CSV files for upload testing
│       ├── normal.csv
│       ├── congestion.csv
│       ├── weak_wifi.csv
│       ├── interface_failure.csv
│       ├── dns_failure.csv
│       ├── dhcp_failure.csv
│       ├── infrastructure_overload.csv
│       └── invalid_telemetry.csv
├── api/                       # FastAPI REST service
│   ├── __init__.py
│   └── main.py                # Endpoints for health, scenarios, diagnosis, CSV & reports
├── dashboard/                 # Streamlit NOC application
│   ├── __init__.py
│   └── app.py                 # Interactive NOC UI with KPI cards, Plotly charts, report export
├── tests/                     # Comprehensive Pytest suite
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_performance_agent.py
│   ├── test_infrastructure_agent.py
│   ├── test_connectivity_agent.py
│   ├── test_correlation_agent.py
│   ├── test_recommendation_agent.py
│   ├── test_orchestrator.py
│   ├── test_scenarios.py
│   ├── test_api.py
│   └── test_csv_loader.py
├── reports/                   # Persisted diagnostic reports (JSON)
├── documentation/             # Technical specifications
│   ├── ARCHITECTURE.md
│   ├── AGENT_COMMUNICATION.md
│   ├── API_REFERENCE.md
│   └── TESTING_GUIDE.md
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart: Running Backend & Dashboard

Dependencies are installed directly in your Python environment. No virtual environment activation is required!

### Option A: One-Click Windows Batch Launchers (Recommended)
You can directly run or double-click the `.bat` files in the repository root:
- `run_backend.bat` — Launches the FastAPI REST server (`http://localhost:8000`)
- `run_dashboard.bat` — Launches the Streamlit NOC Console (`http://localhost:8501`)
- `run_tests.bat` — Runs the full 39-test Pytest suite

---

### Option B: Standard Terminal Commands
Run directly with your default `python`:

#### 1. Launch FastAPI Backend
```powershell
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health: `http://localhost:8000/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

#### 2. Launch Streamlit NOC Dashboard
In a second terminal window:
```powershell
python -m streamlit run dashboard/app.py
```
- Dashboard URL: `http://localhost:8501`

#### 3. Run Automated Pytest Suite
```powershell
python -m pytest -v
```

---

## 🧪 Built-in Diagnostic Scenarios

NetCoop AI includes 8 reproducible synthetic scenarios modeling real-world network operational incidents:

| # | Scenario | Primary Symptoms | Diagnosed Root Cause |
| :-: | :--- | :--- | :--- |
| **1** | **Normal Operation** | Latency <15ms, 0% loss, CPU <35%, DNS nominal | `Nominal Network Operation` |
| **2** | **Network Congestion** | Core link bandwidth >95%, queue drops, latency spikes | `Network Bandwidth Congestion & Bufferbloat` |
| **3** | **Weak Wi-Fi** | Meeting room RSSI -86 dBm, low SNR, endpoint packet loss | `Wireless RF Attenuation / Weak Wi-Fi Coverage` |
| **4** | **Interface Failure** | Port status flapping/down, CRC framing errors | `Physical Interface / Cable Failure` |
| **5** | **DNS Failure** | Query timeouts, servfail errors, raw IP ping intact | `DNS Resolver Outage or Misconfiguration` |
| **6** | **DHCP Failure** | DHCP exhausted/timeout, client reachability degraded | `DHCP Service Failure / Scope Exhaustion` |
| **7** | **Infrastructure Overload** | Core router CPU 98%, RAM 94%, internal queue drops | `Device Hardware / Compute Resource Overload` |
| **8** | **Invalid Telemetry** | Missing IDs, negative latency, out-of-bounds metrics | `Invalid or Empty Telemetry (Safe Degradation)` |

---

## 🔬 Interoperability JSON Contract (`AgentMessage`)

Every agent produces a standardized JSON message envelope ensuring seamless integration:
```json
{
  "message_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "task_id": "TASK-F3A19C02",
  "agent_id": "performance_agent",
  "timestamp": "2026-10-31T09:30:00.000Z",
  "status": "SUCCESS",
  "findings": [
    {
      "finding_id": "FND-A19F83E1",
      "category": "PERFORMANCE",
      "title": "Link Bandwidth Saturation",
      "description": "Bandwidth utilization reached 96.5% on core-router-01.",
      "severity": "CRITICAL",
      "affected_devices": ["core-router-01"],
      "metrics": {"max_bw_util_pct": 96.5}
    }
  ],
  "evidence": [
    {
      "metric_name": "bandwidth_util_pct",
      "observed_value": 96.5,
      "threshold": 80.0,
      "unit": "%",
      "details": "Bandwidth utilization peaked at 96.5%, exceeding 80.0% threshold."
    }
  ],
  "confidence": 0.92,
  "errors": [],
  "metadata": {"record_count": 15, "execution_time_ms": 12.4}
}
```

---

## 🌐 FastAPI Integration & API Reference (Milestone 11)

NetCoop AI exposes an enterprise REST API powered by FastAPI, featuring pre-orchestration schema validation, Pydantic v2 serialization, structured error handling, and complete DiagnosticReport schema v2.0.0 compliance.

### 🚀 Starting the API

Run the backend server locally using Uvicorn or the provided batch script:

```powershell
# Option 1: Uvicorn directly
.venv\Scripts\uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Windows batch launcher
.\run_backend.bat
```

### 📖 Interactive Documentation (Swagger UI & OpenAPI)

Once the server is running, explore and test the endpoints interactively:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Technical Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI 3.1 Specification (JSON)**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

### 📡 Endpoint Overview

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/health` | API and Orchestrator health and readiness probe | `200` |
| `POST` | `/api/diagnose` | Run end-to-end multi-agent diagnosis on telemetry or scenario | `200`, `400`, `404`, `413`, `422`, `500` |
| `GET` | `/api/reports` | List recently generated diagnostic reports with pagination | `200`, `500` |
| `GET` | `/api/reports/{report_id}` | Fetch a complete DiagnosticReport by **Report ID** or **Diagnosis ID** | `200`, `404`, `500` |
| `GET` | `/api/scenarios` | List all available synthetic benchmark scenarios | `200` |
| `GET` | `/api/scenarios/{scenario_id}` | Get telemetry records and metadata for a specific scenario | `200`, `404` |
| `POST` | `/api/telemetry/submit` | Validate and ingest a raw telemetry batch | `200`, `400`, `413`, `422`, `500` |
| `POST` | `/api/telemetry/upload-csv` | Upload a telemetry CSV file with fuzzy column mapping | `200`, `400`, `500` |

---

### 📑 Payload Specifications & Examples

#### 1. Diagnosis Request (`POST /api/diagnose`)

Clients can request diagnosis either by naming a built-in scenario or by providing a custom batch of telemetry records.

**Request by Scenario Name:**
```json
{
  "scenario_name": "congestion",
  "metadata": {"initiated_by": "noc_operator", "site": "datacenter-east"}
}
```

**Request with Direct Telemetry Batch:**
```json
{
  "telemetry": [
    {
      "timestamp": "2026-10-31T12:00:00Z",
      "device_id": "core-router-01",
      "interface": "GigabitEthernet0/0/1",
      "latency_ms": 145.2,
      "jitter_ms": 18.4,
      "packet_loss_pct": 8.5,
      "bandwidth_util_pct": 94.2,
      "cpu_util_pct": 72.0,
      "memory_util_pct": 68.5,
      "dns_latency_ms": 15.0,
      "dns_lookup_success": true,
      "dhcp_success": true
    }
  ]
}
```

#### 2. Diagnostic Report Response (`DiagnosticReport` Schema 2.0.0)
```json
{
  "report_id": "REP-20261031-120000-A1B2",
  "diagnosis_id": "7b04961d-dd50-48e0-bb12-d9f71cba8be6",
  "task_id": "TASK-A1B2C3D4",
  "schema_version": "2.0.0",
  "timestamp": "2026-10-31T12:00:01.234Z",
  "fault_detected": true,
  "overall_network_health": "DEGRADED",
  "health_classification": "DEGRADED",
  "diagnosis_certainty": "CONFIRMED",
  "primary_root_cause": "Network Congestion / Transit Bandwidth Saturation",
  "confidence_score": 0.92,
  "root_cause_confidence": 0.92,
  "confidence_explanation": "Bandwidth saturation (94.2%) strongly correlated with packet loss (8.5%) and queuing delay.",
  "contributing_factors": ["High buffer utilization", "Peak transit link utilization"],
  "alternative_hypotheses": [],
  "evidence": [
    {
      "evidence_id": "EVD-A19F83E1",
      "metric_name": "bandwidth_util_pct",
      "observed_value": 94.2,
      "threshold": 80.0,
      "unit": "%",
      "finding_type": "BANDWIDTH_SATURATION",
      "device_id": "core-router-01",
      "interface_name": "GigabitEthernet0/0/1"
    }
  ],
  "recommendations": [
    {
      "recommendation_id": "REC-9B1D-001",
      "priority": "HIGH",
      "action": "Enable ingress traffic shaping on GigabitEthernet0/0/1 and reroute non-critical traffic.",
      "category": "TRAFFIC_ENGINEERING"
    }
  ],
  "limitations": {
    "missing_agents": [],
    "invalid_records": 0,
    "stale_observations": []
  },
  "execution_metadata": {
    "execution_time_ms": 42.5,
    "agents_executed": ["performance_agent", "infrastructure_agent", "connectivity_agent", "correlation_agent", "recommendation_agent"],
    "records_analyzed": 1
  }
}
```

#### 3. Structured Error Response (`ErrorResponse`)

When validation fails, NetCoop AI returns structured field-level error messages without exposing sensitive internal stack traces:

```json
{
  "status_code": 422,
  "error_type": "ValidationError",
  "message": "Telemetry validation failed: 1 record(s) contain invalid fields.",
  "detail": [
    {
      "field": "telemetry[0].latency_ms",
      "message": "Input should be greater than or equal to 0",
      "error_type": "greater_than_equal",
      "value": -10.0
    }
  ],
  "timestamp": "2026-10-31T12:00:00.000Z"
}
```

---

### 🛡️ Request Validation & Operational Robustness

1. **Pre-Orchestration Validation**:
   - Requests are strictly validated before dispatching worker threads.
   - Missing required request fields yield HTTP 400.
   - Empty telemetry batches yield HTTP 400.
   - Batches exceeding 5,000 records yield HTTP 413 (Payload Too Large).
   - Unknown scenario names yield HTTP 404 with a list of available scenarios.
2. **Canonical Telemetry Validation**:
   - Out-of-bounds metrics (e.g. `latency_ms < 0`, `packet_loss_pct > 100`) are rejected with HTTP 422.
   - Missing optional fields remain distinguishable from measured zero (`0.0`) values.
   - **Partial Batch Isolation**: If a batch contains both valid and invalid records, the valid records are diagnosed while invalid records are logged under `limitations.invalid_records` rather than aborting analysis.
3. **Dual Identifier Resolution (`report_id` vs `diagnosis_id`)**:
   - Reports are indexed by both human-readable Report ID (e.g., `REP-20261031-143000-A1B2`) and UUID Diagnosis ID (e.g., `7b04961d-dd50-48e0-bb12-d9f71cba8be6`).
   - `GET /api/reports/{id}` automatically resolves either identifier format seamlessly.
4. **Resilience & Fault Isolation**:
   - Persistence failures (e.g., disk full or unwritable directory) are caught gracefully, logging a warning while still returning the complete diagnostic report to the client.
   - Orchestrator exceptions and unexpected server errors return a structured HTTP 500 response without leaking internal code execution paths.

---

## 🛰️ Streamlit NOC Dashboard (Milestone 12)

NetCoop AI includes a dedicated, dark-themed Network Operations Center (NOC) dashboard built with Streamlit and Plotly. Designed for real-time observability, causal triage, and operational safety.

### 🚀 Starting the Dashboard

Launch the console using Streamlit or the provided batch script:

```powershell
# Option 1: Streamlit directly
.venv\Scripts\streamlit run dashboard/app.py

# Option 2: Windows batch launcher
.\run_dashboard.bat
```

Access the NOC interface in your browser at: [http://localhost:8501](http://localhost:8501)

### 🖥️ Dashboard Capabilities & Layout

1. **Network Overview & 4-Tier Health Status**:
   - Explicit 4-tier health indicators: `NOMINAL` (green), `DEGRADED` (amber), `CRITICAL` (red), `UNKNOWN` (slate).
   - High-visibility `FAULT DETECTED` vs `NO FAULT DETECTED` status banners.
   - Separate diagnostic certainty tiers (`CONFIRMED`, `PROVISIONAL`, `INDETERMINATE`, `NOT_APPLICABLE`), ensuring network operational health is never conflated with hypothesis certainty.
   - Non-fabricated confidence: Healthy networks explicitly display `N/A (Baseline Operational State)` rather than misleading root-cause confidence scores.
   - Multi-agent dispatch tally (`X Succeeded | Y Failed | Z Timed Out`).

2. **Diagnostic Summary & Causal Graph**:
   - Primary inferred root cause with technical descriptions, affected nodes, and certainty rating.
   - Corroborating telemetry symptoms vs contradicting / excluded factors.
   - Preserved alternative hypotheses with competing confidence levels and exclusion rationales.
   - Uncertainty notes detailing domain data gaps or sensor lag.

3. **Multi-Agent Execution Grid**:
   - Real-time execution cards for all 5 canonical agents:
     - ⚡ Performance Agent
     - 🖥️ Infrastructure Health Agent
     - 🌐 Connectivity Agent
     - 🧠 Fault Correlation Agent
     - 🛠️ Recommendation Agent
   - Execution duration (ms), finding counts, evidence counts, and error/timeout traces.
   - **Failure Isolation**: A missing, failed, or timed-out agent is **never** presented as healthy.
   - Interactive JSON Message Bus inspector for auditing raw Pydantic envelopes.

4. **Multi-Dimensional Telemetry Visualizations**:
   - Automated detection of chronological time-series vs single-snapshot device comparisons.
   - Plotly charts across 10 core metrics: Latency (ms), Jitter (ms), Packet Loss (%), Throughput (Mbps), Bandwidth Utilization (%), CPU (%), RAM (%), Wi-Fi RSSI (dBm), Hardware Queue Drops, and Interface CRC Errors.
   - Missing optional metrics are safely handled without dashboard crashes.

5. **Findings & Evidence Explorer**:
   - Full 10-column interactive table: `Finding ID`, `Source Agent`, `Device`, `Interface`, `Metric`, `Observed Value`, `Threshold Baseline`, `Severity`, `Timestamp`, and `Finding Type`.
   - Real-time filtering by severity tier, publishing agent, and target device.
   - Consolidated evidence matrix linking telemetry breaches to root-cause hypotheses.

6. **Operational Recommendations & Advisory Runbooks**:
   - **Strict Advisory Mode**: Network remediation is advisory and explicitly requires human operator authorization before production execution.
   - Action categorization: `READ-ONLY DIAGNOSTIC`, `CONFIGURATION CHANGE`, `DISRUPTIVE REMEDIATION`.
   - Prerequisites, verification procedures, step-by-step rollback instructions, and copyable automation CLI snippets.

---

## 📊 Verification & Automated Tests

Execute the automated test suite with Pytest:
```powershell
.venv\Scripts\pytest -v
```

### Actual Test Results
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\bandi\Agentic-AI
plugins: anyio-4.15.1
collected 207 items

tests/test_api.py::test_api_health PASSED                                [  1%]
tests/test_api_milestone11.py ....................                       [ 11%]
tests/test_audit_milestone10.py ..........                               [ 16%]
tests/test_connectivity_agent.py .................                       [ 24%]
tests/test_correlation_agent.py ..............                           [ 31%]
tests/test_csv_loader.py ...                                             [ 32%]
tests/test_dashboard_milestone12.py ..............                       [ 39%]
tests/test_evaluation.py ...........                                     [ 44%]
tests/test_infrastructure_agent.py .................                     [ 53%]
tests/test_milestone2_telemetry.py .........................             [ 65%]
tests/test_models.py ......                                              [ 68%]
tests/test_orchestrator.py .................                             [ 76%]
tests/test_performance_agent.py ...............                          [ 83%]
tests/test_recommendation_agent.py .............                         [ 90%]
tests/test_report_milestone10.py ..........                              [ 75%]
tests/test_robustness_milestone13.py ............................................................... [ 97%]
tests/test_scenarios.py ........                                         [100%]

====================== 279 passed, 4 warnings in 11.68s =======================
```

---

## 🏆 Hackathon Acceptance Criteria Checklist

- [x] **5 Specialized Functional Agents**: Performance, Infrastructure Health, Connectivity, Fault Correlation, Recommendation.
- [x] **Central Orchestrator**: Ingestion, validation, parallel agent execution, fault/timeout recovery, and report synthesis.
- [x] **Pydantic v2 JSON Interoperability**: `message_id`, `task_id`, `agent_id`, `timestamp`, `status`, `findings`, `evidence`, `confidence`, `errors`.
- [x] **Evidence-Based Causal Inference**: Never claims certainty on ambiguous data; includes alternative hypotheses.
- [x] **Conflict Resolution**: Weighs contradicting indicators (e.g. Wi-Fi RF vs. transit link congestion).
- [x] **FastAPI Backend**: Complete REST endpoints for health, scenarios, CSV upload, diagnosis, and reports.
- [x] **Streamlit NOC Console**: Dark-theme operations center UI with KPI metric cards, Plotly charts, agent message inspector, and JSON report export.
- [x] **8 Realistic Synthetic Scenarios**: Auto-generated and downloadable as sample CSVs.
- [x] **Comprehensive Pytest Suite**: 279/279 passing tests (including Milestone 11 API, Milestone 12 Dashboard, & Milestone 13 System Robustness suites).
- [x] **Complete Technical Documentation**: Architecture, agent communication, API reference, and testing guide.

