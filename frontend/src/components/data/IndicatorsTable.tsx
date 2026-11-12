import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { expandCollapse, useMotionReduced } from "../../lib/motion";

/**
 * Тип для причины в таблице
 */
type TableCause = {
  id: string;
  name: string;
  impact: number;
  domain: string;
};

/**
 * Тип для KPI в таблице
 */
type TableKpi = {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "alert" | "warn" | "ok";
  trend: number[]; // данные для MiniSpark
  causes: TableCause[];
};

/**
 * Пропсы для IndicatorsTable
 */
type IndicatorsTableProps = {
  kpis: TableKpi[];
};

/**
 * Статус-бейдж класс
 */
const STATUS_CLASS: Record<TableKpi["status"], string> = {
  alert: "badge-alert",
  warn: "badge-warn",
  ok: "badge-ok",
};

/**
 * Статус-лейбл
 */
const STATUS_LABEL: Record<TableKpi["status"], string> = {
  alert: "Отклонение",
  warn: "Внимание",
  ok: "Норма",
};

/**
 * IndicatorsTable — таблица «Показатели».
 * Клик строки → expandCollapse (динамика MiniSpark + причины).
 */
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
      {/* Заголовок */}
      <h3
        style={{
          fontSize: "1.25rem",
          fontWeight: 600,
          color: "var(--text)",
          marginBottom: "1rem",
        }}
      >
        Показатели
      </h3>

      {/* Таблица */}
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
                <td
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                  }}
                >
                  {kpi.value.toLocaleString("ru-RU")} {kpi.unit}
                </td>
                <td>
                  <span className={`badge ${STATUS_CLASS[kpi.status]}`}>
                    {STATUS_LABEL[kpi.status]}
                  </span>
                </td>
                <td>
                  {/* MiniSpark — мини-график тренда */}
                  <svg
                    width="80"
                    height="24"
                    viewBox="0 0 80 24"
                    style={{ display: "block" }}
                  >
                    <polyline
                      points={kpi.trend
                        .map((val, i) => {
                          const x = (i / (kpi.trend.length - 1)) * 80;
                          const y = 24 - (val / Math.max(...kpi.trend)) * 24;
                          return `${x},${y}`;
                        })
                        .join(" ")}
                      fill="none"
                      stroke={
                        kpi.status === "alert"
                          ? "var(--alert)"
                          : kpi.status === "warn"
                          ? "var(--warn)"
                          : "var(--ok)"
                      }
                      strokeWidth="1.5"
                    />
                  </svg>
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>

      {/* Раскрытые детали (accordion) */}
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
                <div
                  style={{
                    padding: "1.5rem",
                    background: "var(--panel-2)",
                    borderRadius: "var(--radius)",
                    marginTop: "0.5rem",
                  }}
                >
                  {/* Динамика */}
                  <h4
                    style={{
                      fontSize: "1rem",
                      fontWeight: 600,
                      color: "var(--text)",
                      marginBottom: "1rem",
                    }}
                  >
                    Динамика показателя
                  </h4>

                  {/* Большой график тренда */}
                  <svg
                    width="100%"
                    height="120"
                    viewBox="0 0 400 120"
                    style={{ display: "block", marginBottom: "1.5rem" }}
                  >
                    <polyline
                      points={kpi.trend
                        .map((val, i) => {
                          const x = (i / (kpi.trend.length - 1)) * 400;
                          const y = 120 - (val / Math.max(...kpi.trend)) * 120;
                          return `${x},${y}`;
                        })
                        .join(" ")}
                      fill="none"
                      stroke={
                        kpi.status === "alert"
                          ? "var(--alert)"
                          : kpi.status === "warn"
                          ? "var(--warn)"
                          : "var(--ok)"
                      }
                      strokeWidth="2"
                    />
                  </svg>

                  {/* Причины */}
                  {kpi.causes.length > 0 && (
                    <>
                      <h4
                        style={{
                          fontSize: "1rem",
                          fontWeight: 600,
                          color: "var(--text)",
                          marginBottom: "0.75rem",
                        }}
                      >
                        Причины отклонения
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        {kpi.causes.map((cause) => (
                          <div
                            key={cause.id}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              padding: "0.75rem",
                              background: "var(--panel)",
                              borderRadius: "var(--radius)",
                              border: "1px solid var(--hair)",
                            }}
                          >
                            <div>
                              <div
                                style={{
                                  fontWeight: 500,
                                  color: "var(--text)",
                                  fontSize: "0.875rem",
                                }}
                              >
                                {cause.name}
                              </div>
                              <div
                                style={{
                                  fontSize: "0.75rem",
                                  color: "var(--muted)",
                                  marginTop: "0.25rem",
                                }}
                              >
                                {cause.domain}
                              </div>
                            </div>
                            <div
                              style={{
                                fontFamily: "var(--font-mono)",
                                fontWeight: 600,
                                fontSize: "0.875rem",
                                color:
                                  cause.impact < 0 ? "var(--alert)" : "var(--ok)",
                              }}
                            >
                              {cause.impact > 0 ? "+" : ""}
                              {cause.impact}%
                            </div>
                          </div>
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