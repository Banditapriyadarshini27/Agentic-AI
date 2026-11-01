import React from "react";
import { motion } from "framer-motion";

interface PageTransitionProps {
  children: React.ReactNode;
  theme?: "ivory" | "ink";
}

const curtainVariants = {
  initial: {
    opacity: 0,
    y: 12,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.45,
      ease: [0.25, 1, 0.5, 1] as [number, number, number, number],
      staggerChildren: 0.05,
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: {
      duration: 0.2,
      ease: [0.76, 0, 0.24, 1] as [number, number, number, number],
    },
  },
};

export const PageTransition: React.FC<PageTransitionProps> = ({ children, theme = "ivory" }) => {
  return (
    <motion.div
      variants={curtainVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={theme === "ink" ? "theme-ink" : "theme-ivory paper-grain"}
      style={{
        minHeight: "calc(100vh - 72px)",
        width: "100%",
        position: "relative",
      }}
    >
      {children}
    </motion.div>
  );
};
