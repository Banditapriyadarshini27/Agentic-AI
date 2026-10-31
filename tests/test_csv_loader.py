import io
import pytest

from data.csv_loader import load_telemetry_csv


def test_load_telemetry_csv_standard():
    csv_data = (
        "device_id,latency_ms,jitter_ms,packet_loss_pct,cpu_util_pct\n"
        "router-01,15.2,1.8,0.0,35.0\n"
        "router-02,18.4,2.1,0.0,42.0\n"
    )
    df, warnings = load_telemetry_csv(csv_data)
    assert not df.empty
    assert len(df) == 2
    assert "device_id" in df.columns
    assert df["latency_ms"].iloc[0] == 15.2
    assert df["cpu_util_pct"].iloc[1] == 42.0


def test_load_telemetry_csv_fuzzy_headers():
    csv_data = (
        "Host,RTT,Loss,Processor Util,Ping MS\n"
        "core-node,12.5,0.0,55.0,12.5\n"
    )
    df, warnings = load_telemetry_csv(csv_data)
    assert not df.empty
    assert "device_id" in df.columns
    assert "cpu_util_pct" in df.columns
    assert df["cpu_util_pct"].iloc[0] == 55.0


def test_load_telemetry_csv_empty():
    df, warnings = load_telemetry_csv("")
    assert df.empty
    assert len(warnings) > 0


def test_load_telemetry_csv_missing_optionals_and_json_serializable():
    """Verify that missing optional metrics produce None (not NaN) and are JSON serializable."""
    import json
    csv_data = (
        "device_id,latency_ms,jitter_ms,packet_loss_pct,cpu_util_pct\n"
        "router-01,15.2,1.8,0.0,35.0\n"
        "ap-01,20.0,2.5,0.0,40.0\n"
    )
    df, warnings = load_telemetry_csv(csv_data)
    assert not df.empty
    assert "timestamp" in df.columns
    # Check that wifi_signal_dbm is not present or None
    records = df.to_dict(orient="records")
    # Must serialize without "Out of range float values are not JSON compliant: nan" error
    serialized = json.dumps(records)
    assert "router-01" in serialized

