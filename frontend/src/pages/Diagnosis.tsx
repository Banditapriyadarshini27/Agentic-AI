import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import type { DiagnosticReport } from "../types/report";
import { MOCK_REPORT_CONGESTION, MOCK_SCENARIOS } from "../services/mockData";
import { apiService } from "../services/api";

export const Diagnosis: React.FC = () => {
  const [report, setReport] = useState<DiagnosticReport>(MOCK_REPORT_CONGESTION);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeScenario, setActiveScenario] = useState<string>("congestion");

  useEffect(() => {
    const cached = localStorage.getItem("netcoop_latest_report");
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        if (parsed && typeof parsed === "object") {
          setReport(parsed);
        }
      } catch (e) {
        console.error("Failed to parse cached report:", e);
      }
    }
  }, []);

  const handleScenarioChange = async (scenarioId: string) => {
    setActiveScenario(scenarioId);
    setIsLoading(true);
    try {
      const { records } = await apiService.getScenarioData(scenarioId);
      const { report: newReport } = await apiService.runDiagnosis(records, scenarioId);
      setReport(newReport);
      localStorage.setItem("netcoop_latest_report", JSON.stringify(newReport));
    } catch (err) {
      console.warn("Could not load scenario diagnosis:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const isNominal = report.overall_network_health === "NOMINAL" || !report.fault_detected;

  // Safe extraction of root cause candidate with bulletproof fallbacks
  const rootCause = report.probable_root_cause || (report as any).selected_root_cause || {
    title: report.fault_detected ? "Network Anomaly Identified" : "Nominal Network Operation",
    description: report.summary || "All evaluated telemetry metrics remain within designated baseline parameters.",
    supporting_symptoms: [],
    contradicting_symptoms: [],
    affected_devices: report.affected_devices || [],
    evidence_references: [],
    confidence: report.confidence_score ?? 0.95,
  };

  const affectedDevices: string[] =
    report.affected_devices && report.affected_devices.length > 0
      ? report.affected_devices
      : rootCause.affected_devices || [];

  const supportingSymptoms: string[] =
    rootCause.supporting_symptoms && rootCause.supporting_symptoms.length > 0
      ? rootCause.supporting_symptoms
      : (rootCause as any).supporting_findings || [];

  const conflictingEvidence: any[] = report.conflicting_evidence || [];
  const uncertaintyNotes: any[] = report.uncertainty_notes || [];
  const alternativeCauses: any[] =
    report.alternative_causes && report.alternative_causes.length > 0
      ? report.alternative_causes
      : (report as any).alternative_hypotheses || [];

  return (
    <PageTransition theme="ivory">
      {/* =========================================================================
          MASTHEAD STRIP
          ========================================================================= */}
      <section
        style={{
          borderBottom: "var(--solid-ink)",
          padding: "1.75rem var(--margin-gutter)",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "2rem",
          alignItems: "baseline",
        }}
      >
        <div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>
            NETWORK HEALTH
          </p>
          <p
            className="serif-subhead"
            style={{
              fontSize: "1.25rem",
              fontWeight: 500,
              marginTop: "0.25rem",
              textDecoration: report.overall_network_health === "CRITICAL" ? "underline" : "none",
            }}
          >
            {report.overall_network_health || (report.fault_detected ? "DEGRADED" : "NOMINAL")}
          </p>
        </div>

        <div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>
            DIAGNOSIS CERTAINTY
          </p>
          <p className="serif-subhead" style={{ fontSize: "1.25rem", marginTop: "0.25rem" }}>
            {report.diagnosis_certainty || "CONFIRMED"}
          </p>
        </div>

        <div>
          <p
            title="Calibrated heuristic score based on evidence weight minus contradiction penalties, not a statistical probability."
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.6875rem",
              opacity: 0.5,
              cursor: "help",
              textDecoration: "underline dotted",
            }}
          >
            HEURISTIC CONFIDENCE ⓘ
          </p>
          <p className="serif-subhead" style={{ fontSize: "1.25rem", marginTop: "0.25rem" }}>
            {isNominal ? (
              <span style={{ opacity: 0.45 }}>N/A (Zero-Fault Rule)</span>
            ) : (
              <span style={{ color: "var(--ink)", fontWeight: 500 }}>
                {Math.round((report.confidence_score ?? (report as any).confidence ?? 0.95) * 100)}%
              </span>
            )}
          </p>
        </div>

        <div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>
            AFFECTED DEVICES
          </p>
          <p className="serif-subhead" style={{ fontSize: "1.25rem", marginTop: "0.25rem" }}>
            {affectedDevices.length > 0 ? (
              `${affectedDevices.length} Nodes Identified`
            ) : (
              <span style={{ opacity: 0.45 }}>None detected</span>
            )}
          </p>
        </div>

        <div style={{ textAlign: "right" }}>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>
            REPORT IDENTIFIER
          </p>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.875rem", marginTop: "0.25rem" }}>
            {report.report_id || report.diagnosis_id || "REP-LIVE"}
          </p>
        </div>
      </section>

      {/* =========================================================================
          SCENARIO DRILL BAR (Instant scenario switching)
          ========================================================================= */}
      <section
        style={{
          borderBottom: "var(--hairline-ink)",
          padding: "0.75rem var(--margin-gutter)",
          display: "flex",
          alignItems: "center",
          gap: "1.5rem",
          flexWrap: "wrap",
          fontSize: "0.8125rem",
          backgroundColor: "rgba(14, 14, 12, 0.02)",
        }}
      >
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.5 }}>
          DRILL SCENARIO:
        </span>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          {MOCK_SCENARIOS.slice(0, 6).map((sc) => (
            <button
              key={sc.id}
              onClick={() => handleScenarioChange(sc.id)}
              disabled={isLoading}
              style={{
                background: "none",
                border: "none",
                fontFamily: "var(--font-mono)",
                fontSize: "0.75rem",
                cursor: "pointer",
                padding: "2px 6px",
                borderBottom: activeScenario === sc.id ? "1.5px solid var(--ink)" : "1px solid transparent",
                opacity: activeScenario === sc.id ? 1 : 0.5,
                fontWeight: activeScenario === sc.id ? 600 : 400,
              }}
            >
              {sc.title.split(" ")[0]} ({sc.id})
            </button>
          ))}
        </div>
        {isLoading && (
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", color: "var(--teal)" }}>
            Correlating evidence...
          </span>
        )}
      </section>

      {/* =========================================================================
          FEATURE COVER STORY: THE PROBABLE ROOT CAUSE
          ========================================================================= */}
      <section
        style={{
          padding: "clamp(3.5rem, 7vw, 6rem) var(--margin-gutter)",
          maxWidth: "1200px",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.75rem",
            letterSpacing: "0.08em",
            opacity: 0.5,
            marginBottom: "1.5rem",
          }}
        >
          PRIMARY CAUSAL CONCLUSION
        </p>

        <h1
          className="serif-display"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 4.8rem)",
            fontWeight: 300,
            lineHeight: 1.08,
            letterSpacing: "-0.025em",
            marginBottom: "2rem",
          }}
        >
          {rootCause.title}
        </h1>

        {/* Affected Devices Tags */}
        {affectedDevices.length > 0 && (
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2.5rem" }}>
            {affectedDevices.map((dev) => (
              <span
                key={dev}
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.8125rem",
                  borderBottom: "1px solid var(--ink)",
                  paddingBottom: "2px",
                }}
              >
                {dev}
              </span>
            ))}
          </div>
        )}

        {/* Causal Chain Narrative Prose */}
        <p
          style={{
            fontSize: "clamp(1.125rem, 1.5vw, 1.375rem)",
            lineHeight: 1.65,
            opacity: 0.85,
            maxWidth: "60ch",
            fontWeight: 300,
          }}
        >
          {rootCause.description}
        </p>
      </section>

      {/* =========================================================================
          EVIDENCE LEDGER: TWO COLUMNS DIVIDED BY 1PX HAIRLINE
          ========================================================================= */}
      <section
        style={{
          borderTop: "var(--solid-ink)",
          padding: "clamp(3.5rem, 5vw, 5rem) var(--margin-gutter)",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "clamp(2.5rem, 5vw, 5rem)",
        }}
      >
        {/* Column 1: Supporting Symptoms */}
        <div style={{ paddingRight: "clamp(1rem, 2vw, 2rem)" }}>
          <p
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              opacity: 0.5,
              marginBottom: "1.75rem",
            }}
          >
            SUPPORTING SYMPTOMS & VERIFIED EVIDENCE
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            {supportingSymptoms.length > 0 ? (
              supportingSymptoms.map((symptom, idx) => (
                <div
                  key={idx}
                  style={{
                    borderTop: "var(--hairline-ink)",
                    paddingTop: "1rem",
                  }}
                >
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.4 }}>
                    INDICATOR 0{idx + 1}
                  </p>
                  <p
                    className="serif-subhead"
                    style={{
                      fontSize: "1.125rem",
                      marginTop: "0.25rem",
                      lineHeight: 1.45,
                    }}
                  >
                    {symptom}
                  </p>
                </div>
              ))
            ) : (
              <div style={{ borderTop: "var(--hairline-ink)", paddingTop: "1rem" }}>
                <p style={{ fontSize: "0.9375rem", opacity: 0.5, fontStyle: "italic" }}>
                  All telemetry metrics observed within nominal operating baselines.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Column 2: What Argues Against It / Contradictions */}
        <div
          style={{
            borderLeft: "var(--hairline-ink)",
            paddingLeft: "clamp(1.5rem, 3vw, 3rem)",
          }}
        >
          <p
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              opacity: 0.5,
              marginBottom: "1.75rem",
            }}
          >
            WHAT ARGUES AGAINST IT & PENALTIES
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            {conflictingEvidence.length > 0 ? (
              conflictingEvidence.map((conf: any, idx: number) => {
                const isObj = typeof conf === "object" && conf !== null;
                const title = isObj
                  ? conf.type || conf.conflict_id || `CONTRADICTION ANALYSIS 0${idx + 1}`
                  : `CONTRADICTION ANALYSIS 0${idx + 1}`;
                const text = isObj
                  ? conf.resolution || conf.finding_a || conf.finding_b || JSON.stringify(conf)
                  : String(conf);
                const penalty =
                  isObj && conf.confidence_penalty
                    ? `Penalty: -${Math.round(conf.confidence_penalty * 100)}%`
                    : null;

                return (
                  <div
                    key={idx}
                    style={{
                      borderTop: "var(--hairline-ink)",
                      paddingTop: "1rem",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.4 }}>
                        {title}
                      </p>
                      {penalty && (
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.6875rem",
                            color: "var(--ink)",
                            fontWeight: 500,
                          }}
                        >
                          {penalty}
                        </span>
                      )}
                    </div>
                    <p
                      style={{
                        fontSize: "0.9375rem",
                        marginTop: "0.25rem",
                        lineHeight: 1.5,
                        opacity: 0.85,
                      }}
                    >
                      {text}
                    </p>
                    {isObj && conf.agent_a && conf.agent_b && (
                      <p
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.6875rem",
                          opacity: 0.5,
                          marginTop: "0.4rem",
                        }}
                      >
                        Source domains: {conf.agent_a} vs {conf.agent_b}
                      </p>
                    )}
                  </div>
                );
              })
            ) : (
              <p style={{ fontSize: "0.9375rem", opacity: 0.5, fontStyle: "italic", paddingTop: "0.5rem" }}>
                No conflicting observations identified across domain agents.
              </p>
            )}

            {uncertaintyNotes.map((note: any, idx: number) => {
              const text =
                typeof note === "object" && note !== null
                  ? note.text || note.note || note.explanation || JSON.stringify(note)
                  : String(note);

              return (
                <div
                  key={idx}
                  style={{
                    borderTop: "var(--hairline-ink)",
                    paddingTop: "1rem",
                  }}
                >
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.6875rem", opacity: 0.4 }}>
                    CALIBRATION NOTE 0{idx + 1}
                  </p>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      marginTop: "0.25rem",
                      lineHeight: 1.5,
                      opacity: 0.75,
                    }}
                  >
                    {text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================================
          ALTERNATIVE HYPOTHESES LIST (When available)
          ========================================================================= */}
      {alternativeCauses.length > 0 && (
        <section
          style={{
            borderTop: "var(--hairline-ink)",
            padding: "clamp(3.5rem, 5vw, 5rem) var(--margin-gutter)",
          }}
        >
          <p
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              opacity: 0.5,
              marginBottom: "2rem",
            }}
          >
            ALTERNATIVE HYPOTHESES EVALUATED & DEPRIORITIZED
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
            {alternativeCauses.map((alt: any, idx: number) => (
              <div
                key={idx}
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 200px",
                  gap: "3rem",
                  paddingBottom: "2rem",
                  borderBottom: "var(--hairline-ink)",
                  alignItems: "baseline",
                }}
              >
                <div>
                  <h3 className="serif-subhead" style={{ fontSize: "1.375rem" }}>
                    {alt.title}
                  </h3>
                  <p style={{ fontSize: "0.9375rem", opacity: 0.75, marginTop: "0.4rem", maxWidth: "60ch" }}>
                    {alt.description}
                  </p>
                  <p
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.75rem",
                      opacity: 0.5,
                      marginTop: "0.5rem",
                    }}
                  >
                    Reason Deprioritized:{" "}
                    {(alt.contradicting_symptoms || []).join("; ") || "Insufficient corroborating telemetry evidence."}
                  </p>
                </div>

                <div>
                  <div
                    style={{
                      height: "1px",
                      backgroundColor: "var(--ink-15)",
                      width: "100%",
                      marginBottom: "0.5rem",
                      position: "relative",
                    }}
                  >
                    <div
                      style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        height: "1px",
                        backgroundColor: "var(--ink)",
                        width: `${Math.round((alt.confidence || 0) * 100)}%`,
                      }}
                    />
                  </div>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", opacity: 0.6 }}>
                    Weight: {Math.round((alt.confidence || 0) * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* =========================================================================
          PERSISTENT EDITORIAL NAVIGATION SECTION (Always Rendered)
          ========================================================================= */}
      <section
        style={{
          borderTop: "var(--solid-ink)",
          padding: "3rem var(--margin-gutter)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1.5rem",
          backgroundColor: "rgba(14, 14, 12, 0.015)",
        }}
      >
        <div style={{ display: "flex", gap: "2rem", alignItems: "center" }}>
          <Link
            to="/pipeline"
            className="editorial-link"
            style={{ fontSize: "0.875rem", opacity: 0.75 }}
          >
            ← Review Agent Reasoning Pipeline
          </Link>
          <Link
            to="/telemetry"
            className="editorial-link"
            style={{ fontSize: "0.875rem", opacity: 0.75 }}
          >
            Inspect Telemetry Series
          </Link>
        </div>

        <Link
          to="/runbook"
          className="editorial-link"
          style={{
            fontSize: "1rem",
            fontWeight: 500,
            borderBottom: "1.5px solid var(--ink)",
            paddingBottom: "3px",
          }}
        >
          Proceed to Safety-Gated Runbook Actions →
        </Link>
      </section>
    </PageTransition>
  );
};
