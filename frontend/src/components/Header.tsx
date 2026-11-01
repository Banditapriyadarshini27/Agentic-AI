import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { apiService } from "../services/api";

export const Header: React.FC = () => {
  const location = useLocation();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const checkApi = async () => {
      const health = await apiService.checkHealth();
      if (mounted) {
        setApiOnline(!health.isMock && health.status === "healthy");
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { label: "Incident", path: "/" },
    { label: "Ingest", path: "/ingest" },
    { label: "Pipeline", path: "/pipeline" },
    { label: "Diagnosis", path: "/diagnosis" },
    { label: "Runbook", path: "/runbook" },
    { label: "Telemetry", path: "/telemetry" },
    { label: "Vault", path: "/vault" },
  ];

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 500,
        backdropFilter: "blur(12px)",
        backgroundColor: "rgba(244, 239, 230, 0.88)",
        borderBottom: "var(--hairline-ink)",
        padding: "1.25rem var(--margin-gutter)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        transition: "background-color 0.4s ease, border-color 0.4s ease",
      }}
    >
      {/* Brand Wordmark in Serif Italic */}
      <Link
        to="/"
        style={{
          textDecoration: "none",
          color: "var(--ink)",
          display: "flex",
          alignItems: "baseline",
          gap: "0.75rem",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-serif)",
            fontStyle: "italic",
            fontSize: "1.5rem",
            fontWeight: 400,
            letterSpacing: "-0.02em",
          }}
        >
          NetCoop
        </span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.6875rem",
            opacity: 0.5,
            letterSpacing: "0.05em",
          }}
        >
          NOC / ISSUE 13
        </span>
      </Link>

      {/* Navigation Links with animated 400ms drawing underlines */}
      <nav
        style={{
          display: "flex",
          alignItems: "center",
          gap: "clamp(1rem, 2.5vw, 2.25rem)",
        }}
      >
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`editorial-link ${isActive ? "active" : ""}`}
              style={{
                fontSize: "0.875rem",
                fontWeight: isActive ? 500 : 400,
                color: "var(--ink)",
                opacity: isActive ? 1 : 0.7,
                paddingBottom: "2px",
              }}
            >
              {item.label}
            </Link>
          );
        })}

        {/* Quiet API Heartbeat Status */}
        <div
          title={apiOnline ? "FastAPI Multi-Agent Engine Online" : "Local Autonomous Mode"}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginLeft: "0.5rem",
            paddingLeft: "1rem",
            borderLeft: "var(--hairline-ink)",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--teal)",
              opacity: apiOnline ? 1 : 0.4,
              boxShadow: apiOnline ? "0 0 6px rgba(0, 229, 199, 0.4)" : "none",
              display: "inline-block",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.6875rem",
              opacity: 0.6,
              letterSpacing: "0.02em",
            }}
          >
            {apiOnline ? "online" : "offline"}
          </span>
        </div>
      </nav>
    </header>
  );
};
