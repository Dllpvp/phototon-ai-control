import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { expandCollapse, useMotionReduced } from "../../lib/motion";
import type { DecisionAlert } from "../../lib/adapters";

type RequiresDecisionProps = {
  alerts: DecisionAlert[];
  onDecision?: (alert: DecisionAlert) => void;
};

export function RequiresDecision({ alerts, onDecision }: RequiresDecisionProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const reduced = useMotionReduced();

  const toggleCard = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  if (alerts.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <p style={{ color: "var(--muted)" }}>Нет алертов, требующих решения</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: "1.5rem" }}>
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>
        Требуют решения
      </h3>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {alerts.map((alert) => {
          const isExpanded = expandedId === alert.id;

          return (
            <div key={alert.id}>
              <motion.div
                className="kpi-card"
                onClick={() => toggleCard(alert.id)}
                style={{ borderLeft: "4px solid var(--alert)", padding: "1rem" }}
                whileHover={!reduced ? { scale: 1.01 } : undefined}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.95rem", marginBottom: "0.25rem" }}>
                      {alert.kpiName}
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.4 }}>
                      {alert.description}
                    </div>
                  </div>

                  <div style={{ fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: "1.1rem", color: "var(--alert)", marginLeft: "1rem" }}>
                    {alert.costPerDay} BYN/день
                  </div>
                </div>

                <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.75rem", fontSize: "0.75rem", color: "var(--muted)" }}>
                  <span className="badge badge-alert">Неделя {alert.week}</span>
                </div>
              </motion.div>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    variants={reduced ? undefined : expandCollapse}
                    initial="collapsed"
                    animate="expanded"
                    exit="collapsed"
                    style={{ overflow: "hidden" }}
                  >
                    <div style={{ padding: "1rem", background: "var(--panel-2)", borderRadius: "0 0 var(--radius) var(--radius)", marginTop: "-0.5rem", borderTop: "1px solid var(--hair)" }}>
                      <p style={{ fontSize: "0.875rem", color: "var(--text)", marginBottom: "1rem", lineHeight: 1.5 }}>
                        {alert.description}
                      </p>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDecision?.(alert);
                        }}
                        style={{ width: "100%", padding: "0.6rem", background: "var(--accent)", color: "var(--text)", border: "none", borderRadius: "var(--radius)", fontWeight: 600, fontSize: "0.875rem", cursor: "pointer" }}
                      >
                        Оформить решение
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}