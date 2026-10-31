import React, { useEffect, useState } from "react";

export const Cursor: React.FC = () => {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [isHovering, setIsHovering] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });

      // Check if hovering interactive element
      const target = e.target as HTMLElement | null;
      if (target) {
        const interactive = target.closest("a, button, input, select, textarea, [data-interactive='true'], .editorial-link");
        setIsHovering(!!interactive);

        // Check if cursor is over a dark section
        const darkSection = target.closest(".theme-ink");
        setIsDark(!!darkSection);
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    return () => window.removeEventListener("mousemove", onMouseMove);
  }, []);

  return (
    <>
      <div
        className={`custom-cursor-dot ${isDark ? "on-dark" : ""}`}
        style={{ left: `${pos.x}px`, top: `${pos.y}px` }}
      />
      <div
        className={`custom-cursor-ring ${isHovering ? "active" : ""}`}
        style={{ left: `${pos.x}px`, top: `${pos.y}px` }}
      />
    </>
  );
};
