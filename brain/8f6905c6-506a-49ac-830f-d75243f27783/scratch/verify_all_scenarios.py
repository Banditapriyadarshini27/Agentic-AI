import sys
sys.path.insert(0, r"c:\Users\bandi\Agentic-AI")

from orchestrator.orchestrator import CentralOrchestrator
from data.scenarios import SCENARIO_METADATA, generate_scenario_data
from diagnosis.models import NetworkHealthStatus

orch = CentralOrchestrator()

print("=== SCENARIO END-TO-END DIAGNOSTIC AUDIT ===")
results = []
for sc_id, meta in SCENARIO_METADATA.items():
    data = generate_scenario_data(sc_id)
    report = orch.run_diagnosis(data, scenario_name=sc_id, save_report=False)
    
    root_cause_title = report.probable_root_cause.title if report.probable_root_cause else "None"
    status_pass = (
        report.overall_network_health == NetworkHealthStatus.HEALTHY if sc_id == "normal"
        else (report.overall_status == "FAILED" if sc_id == "invalid_telemetry" else report.fault_detected is True)
    )
    
    recs_count = len(report.recommended_corrective_actions or report.recommendations or [])
    disruptive_count = sum(1 for r in (report.recommended_corrective_actions or []) if r.requires_human_approval)
    
    res_line = {
        "scenario": sc_id,
        "title": meta["title"],
        "records": len(data),
        "health": report.overall_network_health.value if hasattr(report.overall_network_health, "value") else str(report.overall_network_health),
        "certainty": report.diagnosis_certainty,
        "confidence": round(report.confidence_score, 2),
        "root_cause": root_cause_title,
        "affected_devices": len(report.affected_devices),
        "recommendations": recs_count,
        "human_approval_required": disruptive_count,
        "pass": status_pass
    }
    results.append(res_line)
    status_str = "PASS" if status_pass else "FAIL"
    print(f"[{status_str}] {sc_id:25s} | Health: {res_line['health']:8s} | Cert: {res_line['certainty']:12s} | Conf: {res_line['confidence']:4.2f} | Devices: {res_line['affected_devices']:2d} | Recs: {recs_count:1d} (Gated: {disruptive_count:1d}) | Cause: {root_cause_title[:35]}")

all_pass = all(r["pass"] for r in results)
print(f"\nALL SCENARIOS PASS VERIFICATION: {all_pass}")
