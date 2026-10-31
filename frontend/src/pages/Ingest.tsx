import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import {
  RouterIllustration,
  CableIllustration,
  AntennaIllustration,
  CompassIllustration,
  LighthouseIllustration,
  MagnifierIllustration,
} from "../components/Illustrations";
import { apiService } from "../services/api";
import type { ScenarioDefinition, TelemetryRecord } from "../types/telemetry";

export const Ingest: React.FC = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<ScenarioDefinition[]>([]);
  const [hoveredScenario, setHoveredScenario] = useState<string | null>("congestion");
  const [dragActive, setDragActive] = useState(false);
  const [uploadedRecords, setUploadedRecords] = useState<TelemetryRecord[] | null>(null);
  const [csvStats, setCsvStats] = useState<{
    total: number;
    devices: string[];
    warnings: string[];
    quarantined: number;
  } | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    apiService.getScenarios().then((res) => setScenarios(res.scenarios));
  }, []);

  const handleSelectScenario = async (scenarioId: string) => {
    setIsProcessing(true);
    try {
      const dataRes = await apiService.getScenarioData(scenarioId);
      const diagRes = await apiService.runDiagnosis(dataRes.records, scenarioId);
      localStorage.setItem("netcoop_latest_report", JSON.stringify(diagRes.report));
      navigate("/diagnosis");
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadCsv = (scenarioId: string) => {
    window.open(`http://127.0.0.1:8000/api/scenarios/${scenarioId}/csv`, "_blank");
  };

  // CSV Drag and drop / parse handler
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        parseCsv(text);
      };
      reader.readAsText(file);
    }
  };

  const parseCsv = (csvText: string) => {
    const lines = csvText.trim().split("\n");
    if (lines.length < 2) return;

    const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
    const records: TelemetryRecord[] = [];
    const devices = new Set<string>();
    const warnings: string[] = [];
    let quarantined = 0;

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",").map((v) => v.trim().replace(/^"|"$/g, ""));
      if (values.length !== headers.length) continue;

      const record: any = {};
      headers.forEach((h, idx) => {
        const val = values[idx];
        const num = parseFloat(val);
        record[h] = isNaN(num) ? val : num;
      });

      if (!record.device_id) {
        quarantined++;
        warnings.push(`Row ${i}: Missing device_id, record quarantined.`);
        continue;
      }

      // Check bounds
      if (typeof record.packet_loss_pct === "number" && (record.packet_loss_pct < 0 || record.packet_loss_pct > 100)) {
        quarantined++;
        warnings.push(`Row ${i}: packet_loss_pct out of bounds [0, 100], quarantined.`);
        continue;
      }

      devices.add(record.device_id);
      records.push(record);
    }

    setUploadedRecords(records);
    setCsvStats({
      total: records.length,
      devices: Array.from(devices),
      warnings: warnings.slice(0, 4),
      quarantined,
    });
  };

  const handleDiagnoseUploaded = async () => {
    if (!uploadedRecords) return;
    setIsProcessing(true);
    try {
      const diagRes = await apiService.runDiagnosis(uploadedRecords, "custom_csv");
      localStorage.setItem("netcoop_latest_report", JSON.stringify(diagRes.report));
      navigate("/diagnosis");
    } finally {
      setIsProcessing(false);
    }
  };

  const renderIllustration = (id: string | null) => {
    switch (id) {
      case "congestion":
        return <RouterIllustration size={160} color="var(--ink)" />;
      case "weak_wifi":
        return <AntennaIllustration size={160} color="var(--ink)" />;
      case "interface_failure":
        return <CableIllustration size={160} color="var(--ink)" />;
      case "dns_failure":
      case "dhcp_failure":
        return <CompassIllustration size={160} color="var(--ink)" />;
      case "infrastructure_overload":
        return <MagnifierIllustration size={160} color="var(--ink)" />;
      default:
        return <LighthouseIllustration size={160} color="var(--ink)" />;
    }
  };

  return (
    <PageTransition theme="ivory">
      <div style={{ padding: "clamp(3rem, 6vw, 6rem) var(--margin-gutter)" }}>
        {/* Header */}
        <div style={{ maxWidth: "800px", marginBottom: "4rem" }}>
          <p
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              opacity: 0.5,
              marginBottom: "1rem",
            }}
          >
            INGESTION STUDIO
          </p>
          <h1
            className="serif-headline"
            style={{
              fontSize: "clamp(2.4rem, 4.5vw, 4.2rem)",
              marginBottom: "1rem",
            }}
          >
            Telemetry Ingest & Scenario Index
          </h1>
          <p style={{ opacity: 0.7, maxWidth: "56ch", fontSize: "1.0625rem" }}>
            Examine standardized test scenarios from the benchmark suite or drop an operational CSV telemetry stream for automated validation and causal deduction.
          </p>
        </div>

        {/* Section 1: CSV Ruled Drop Zone */}
        <div style={{ marginBottom: "5rem" }}>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            style={{
              minHeight: "220px",
              border: dragActive ? "1.5px solid var(--teal)" : "var(--hairline-ink)",
              padding: "3rem",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "flex-start",
              transition: "border 0.3s ease",
              position: "relative",
            }}
          >
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", opacity: 0.5 }}>
              TELEMETRY INGESTION PORT
            </p>
            <p className="serif-subhead" style={{ fontSize: "1.5rem", marginTop: "0.5rem" }}>
              Drag and drop an operational telemetry CSV file here
            </p>
            <p style={{ fontSize: "0.875rem", opacity: 0.6, marginTop: "0.25rem", maxWidth: "60ch" }}>
              Accepts RFC-4180 CSV with device_id, timestamp, and standard performance, infrastructure, or connectivity metrics.
            </p>

            {csvStats && (
              <div
                style={{
                  marginTop: "2rem",
                  paddingTop: "1.5rem",
                  borderTop: "var(--hairline-ink)",
                  width: "100%",
                  display: "grid",
                  gridTemplateColumns: "repeat(4, 1fr)",
                  gap: "2rem",
                }}
              >
                <div>
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>PARSED RECORDS</p>
                  <p className="serif-subhead" style={{ fontSize: "1.25rem" }}>{csvStats.total}</p>
                </div>
                <div>
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>DEVICE DOMAIN</p>
                  <p className="serif-subhead" style={{ fontSize: "1.25rem" }}>{csvStats.devices.length} Devices</p>
                </div>
                <div>
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>QUARANTINED</p>
                  <p className="serif-subhead" style={{ fontSize: "1.25rem" }}>{csvStats.quarantined} Records</p>
                </div>
                <div>
                  <button
                    onClick={handleDiagnoseUploaded}
                    disabled={isProcessing}
                    style={{
                      padding: "0.6rem 1.25rem",
                      backgroundColor: "var(--ink)",
                      color: "var(--ivory)",
                      border: "none",
                      fontFamily: "var(--font-sans)",
                      fontSize: "0.8125rem",
                      cursor: "pointer",
                      width: "100%",
                      textAlign: "center",
                    }}
                  >
                    {isProcessing ? "Diagnosing..." : "Run Multi-Agent Diagnosis"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Section 2: Scenario Catalog as Typographic Table of Contents */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 220px", gap: "4rem" }}>
          <div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "60px 1fr 240px",
                paddingBottom: "1rem",
                borderBottom: "var(--solid-ink)",
                fontFamily: "var(--font-mono)",
                fontSize: "0.6875rem",
                letterSpacing: "0.08em",
                opacity: 0.5,
              }}
            >
              <span>INDEX</span>
              <span>SCENARIO & DIAGNOSTIC OBJECTIVE</span>
              <span style={{ textAlign: "right" }}>ACTIONS</span>
            </div>

            {scenarios.map((sc, idx) => (
              <div
                key={sc.id}
                onMouseEnter={() => setHoveredScenario(sc.id)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "60px 1fr 240px",
                  padding: "1.75rem 0",
                  borderBottom: "var(--hairline-ink)",
                  alignItems: "baseline",
                }}
              >
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8125rem", opacity: 0.4 }}>
                  0{idx + 1}
                </span>

                <div style={{ paddingRight: "2rem" }}>
                  <h3 className="serif-subhead" style={{ fontSize: "1.375rem", fontWeight: 400 }}>
                    {sc.title}
                  </h3>
                  <p style={{ fontSize: "0.875rem", opacity: 0.65, marginTop: "0.35rem", lineHeight: 1.5 }}>
                    {sc.description}
                  </p>
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.45, marginTop: "0.25rem" }}>
                    Expected: {sc.expected_root_cause}
                  </p>
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "1.5rem" }}>
                  <button
                    onClick={() => handleSelectScenario(sc.id)}
                    className="editorial-link"
                    style={{
                      background: "none",
                      border: "none",
                      padding: 0,
                      fontFamily: "var(--font-sans)",
                      fontSize: "0.8125rem",
                      fontWeight: 500,
                      color: "var(--ink)",
                      cursor: "pointer",
                    }}
                  >
                    Load & analyse
                  </button>
                  <button
                    onClick={() => handleDownloadCsv(sc.id)}
                    className="editorial-link"
                    style={{
                      background: "none",
                      border: "none",
                      padding: 0,
                      fontFamily: "var(--font-sans)",
                      fontSize: "0.8125rem",
                      color: "var(--ink)",
                      opacity: 0.7,
                      cursor: "pointer",
                    }}
                  >
                    Download CSV
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Marginal Illustration that updates on row hover */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "3rem" }}>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.4, marginBottom: "1.5rem" }}>
              ARCHITECTURAL ENGRAVING
            </p>
            {renderIllustration(hoveredScenario)}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};
