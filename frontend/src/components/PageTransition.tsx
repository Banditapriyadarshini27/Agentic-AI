import React from "react";
import { motion } from "framer-motion";

interface PageTransitionProps {
  children: React.ReactNode;
  theme?: "ivory" | "ink";
}

const curtainVariants = {
  initial: {
    opacity: 0,
    y: 16,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.7,
      ease: [0.76, 0, 0.24, 1] as [number, number, number, number],
      staggerChildren: 0.08,
    },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: {
      duration: 0.4,
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
