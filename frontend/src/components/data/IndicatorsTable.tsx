import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { expandCollapse, useMotionReduced } from "../../lib/motion";
import type { TableKpi, ChainCause } from "../../lib/adapters";

type IndicatorsTableProps = {
  kpis: TableKpi[];
};

const STATUS_CLASS: Record<TableKpi["status"], string> = {
  red: "badge-alert",
  yellow: "badge-warn",
  green: "badge-ok",
};

const STATUS_LABEL: Record<TableKpi["status"], string> = {
  red: "Отклонение",
  yellow: "Внимание",
  green: "Норма",
};

export function IndicatorsTable({ kpis }: IndicatorsTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const reduced = useMotionReduced();

  const toggleRow = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  if (kpis.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <p style={{ color: "var(--muted)" }}>Показатели не найдены</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: "1.5rem" }}>
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>
        Показатели
      </h3>

      <table className="indicators-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Значение</th>
            <th>Статус</th>
            <th>Динамика</th>
          </tr>
        </thead>
        <tbody>
          {kpis.map((kpi) => {
            const isExpanded = expandedId === kpi.id;

            return (
              <motion.tr
                key={kpi.id}
                onClick={() => toggleRow(kpi.id)}
                className={isExpanded ? "expanded" : ""}
                style={{ cursor: "pointer" }}
                whileHover={!reduced ? { backgroundColor: "var(--panel-2)" } : undefined}
              >
                <td style={{ fontWeight: 500 }}>{kpi.name}</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600 }}>
                  {kpi.value.toLocaleString("ru-RU")} {kpi.unit}
                </td>
                <td>
                  <span className={`badge ${STATUS_CLASS[kpi.status]}`}>
                    {STATUS_LABEL[kpi.status]}
                  </span>
                </td>
                <td>
                  {/* MiniSpark — показываем только если trend загружен */}
                  {kpi.trend && kpi.trend.length > 0 ? (
                    <svg width="80" height="24" viewBox="0 0 80 24" style={{ display: "block" }}>
                      <polyline
                        points={kpi.trend
                          .map((val, i) => {
                            const max = Math.max(...kpi.trend!);
                            const x = (i / (kpi.trend!.length - 1)) * 80;
                            const y = 24 - (val / max) * 24;
                            return `${x},${y}`;
                          })
                          .join(" ")}
                        fill="none"
                        stroke={
                          kpi.status === "red"
                            ? "var(--alert)"
                            : kpi.status === "yellow"
                            ? "var(--warn)"
                            : "var(--ok)"
                        }
                        strokeWidth="1.5"
                      />
                    </svg>
                  ) : (
                    <span style={{ color: "var(--muted)", fontSize: "0.75rem" }}>—</span>
                  )}
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>

      <AnimatePresence>
        {kpis.map((kpi) => {
          const isExpanded = expandedId === kpi.id;

          return (
            <motion.div
              key={`detail-${kpi.id}`}
              variants={reduced ? undefined : expandCollapse}
              initial="collapsed"
              animate={isExpanded ? "expanded" : "collapsed"}
              exit="collapsed"
              style={{ overflow: "hidden" }}
            >
              {isExpanded && (
                <div style={{ padding: "1.5rem", background: "var(--panel-2)", borderRadius: "var(--radius)", marginTop: "0.5rem" }}>
                  <h4 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>
                    Динамика показателя
                  </h4>

                  {kpi.trend && kpi.trend.length > 0 ? (
                    <svg width="100%" height="120" viewBox="0 0 400 120" style={{ display: "block", marginBottom: "1.5rem" }}>
                      <polyline
                        points={kpi.trend
                          .map((val, i) => {
                            const max = Math.max(...kpi.trend!);
                            const x = (i / (kpi.trend!.length - 1)) * 400;
                            const y = 120 - (val / max) * 120;
                            return `${x},${y}`;
                          })
                          .join(" ")}
                        fill="none"
                        stroke={
                          kpi.status === "red"
                            ? "var(--alert)"
                            : kpi.status === "yellow"
                            ? "var(--warn)"
                            : "var(--ok)"
                        }
                        strokeWidth="2"
                      />
                    </svg>
                  ) : (
                    <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
                      Данные динамики не загружены
                    </p>
                  )}

                  {kpi.causes && kpi.causes.length > 0 && (
                    <>
                      <h4 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text)", marginBottom: "0.75rem" }}>
                        Причины отклонения
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        {kpi.causes.map((cause) => (
                          <CauseRow key={cause.id} cause={cause} />
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

function CauseRow({ cause }: { cause: ChainCause }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", background: "var(--panel)", borderRadius: "var(--radius)", border: "1px solid var(--hair)" }}>
      <div>
        <div style={{ fontWeight: 500, color: "var(--text)", fontSize: "0.875rem" }}>{cause.name}</div>
        <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.25rem" }}>{cause.domain}</div>
      </div>
      <div style={{ fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: "0.875rem", color: "var(--text)" }}>
        {cause.value} {cause.unit}
      </div>
    </div>
  );
}