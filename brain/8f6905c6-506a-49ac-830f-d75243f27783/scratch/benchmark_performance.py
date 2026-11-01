import time
import math
import tracemalloc
import sys
import os

sys.path.insert(0, r"c:\Users\bandi\Agentic-AI")

import pandas as pd
from datetime import datetime, timezone, timedelta
from orchestrator.orchestrator import CentralOrchestrator

orch = CentralOrchestrator()

def make_batch(num_devices, steps=10):
    now = datetime.now(timezone.utc)
    records = []
    for d in range(num_devices):
        dev_id = f"dev-{d:03d}"
        for s in range(steps):
            records.append({
                "timestamp": (now - timedelta(seconds=s*10)).isoformat(),
                "device_id": dev_id,
                "latency_ms": 15.0 + (d % 3) * 2.0,
                "jitter_ms": 1.5,
                "packet_loss_pct": 0.0,
                "cpu_util_pct": 25.0 + (d % 5),
                "bandwidth_util_pct": 40.0,
                "interface_status": "up",
                "interface_errors": 0,
                "queue_drops": 0
            })
    return records

tracemalloc.start()
benchmarks = {}

print("=== NETCOOP AI PERFORMANCE BENCHMARK ===")
for n in [1, 10, 50, 100]:
    batch = make_batch(n)
    tracemalloc.reset_peak()
    t0 = time.perf_counter()
    report = orch.run_diagnosis(batch, scenario_name=f"bench-{n}", save_report=False)
    t1 = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    
    total_ms = (t1 - t0) * 1000
    benchmarks[n] = {
        "devices": n,
        "records": len(batch),
        "duration_ms": round(total_ms, 2),
        "peak_mem_mb": round(peak_mem / 1024 / 1024, 2),
        "health": str(report.overall_network_health),
        "successful_agents": report.successful_agents,
        "agent_summary": report.agent_execution_summary
    }
    print(f"Devices: {n:3d} | Records: {len(batch):5d} | Latency: {total_ms:6.1f}ms | Peak Mem: {peak_mem / 1024 / 1024:5.2f}MB")

print("\n=== DETAILED 100-DEVICE BREAKDOWN (1,000 Records) ===")
for ag, details in benchmarks[100]["agent_summary"].items():
    print(f"  Agent: {ag:25s} | Execution: {details.get('duration_ms', 0):6.1f}ms | Status: {details.get('status', 'OK')}")
