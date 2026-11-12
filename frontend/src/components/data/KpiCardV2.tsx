import { motion } from "framer-motion";
import { containerTransform, fadeIn, useMotionReduced } from "../../lib/motion";
import { KpiData } from "../../lib/adapters";

type KpiCardV2Props = {
  kpi: KpiData;
  onClick?: () => void;
};

export function KpiCardV2({ kpi, onClick }: KpiCardV2Props) {
  const reduced = useMotionReduced();

  const statusLabel: Record<KpiData["status"], string> = {
    alert: "Отклонение",
    warn: "Внимание",
    ok: "Норма",
  } as Record<KpiData["status"], string>;

  const statusClass: Record<KpiData["status"], string> = {
    red: "badge-alert",
    yellow: "badge-warn",
    green: "badge-ok",
  };

  const labelMap: Record<KpiData["status"], string> = {
    red: "Отклонение",
    yellow: "Внимание",
    green: "Норма",
  };

  return (
    <motion.div
      className="kpi-card"
      onClick={onClick}
      layoutId={`kpi-card-${kpi.id}`}
      variants={reduced ? undefined : fadeIn}
      whileHover={!reduced ? { scale: 1.02 } : undefined}
      whileTap={!reduced ? { scale: 0.98 } : undefined}
      style={{ cursor: onClick ? "pointer" : "default" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div className="kpi-label">{kpi.name}</div>
        <span className={`badge ${statusClass[kpi.status]}`}>
          {labelMap[kpi.status]}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
        <div className="kpi-value">{kpi.value.toLocaleString("ru-RU")}</div>
        <div className="kpi-unit">{kpi.unit}</div>
      </div>

      {/* Bar-график периодов — только если periods загружены */}
      {kpi.periods && kpi.periods.length > 0 ? (
        <div className="waterfall" style={{ height: "60px", marginTop: "1rem" }}>
          {kpi.periods.map((period) => {
            const maxValue = Math.max(...kpi.periods!.map((p) => Math.abs(p.value)));
            const height = maxValue > 0 ? (Math.abs(period.value) / maxValue) * 100 : 0;

            return (
              <div
                key={period.period}
                className="waterfall-bar neutral"
                style={{ height: `${height}%` }}
              >
                <div className="bar-label">{period.period}</div>
              </div>
            );
          })}
        </div>
      ) : (
        <div
          style={{
            height: "60px",
            marginTop: "1rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--muted)",
            fontSize: "0.75rem",
            background: "var(--panel-2)",
            borderRadius: "var(--radius)",
          }}
        >
          Данные периодов не загружены
        </div>
      )}
    </motion.div>
  );
}

type KpiDetailV2Props = {
  kpi: KpiData;
  onClose: () => void;
};

export function KpiDetailV2({ kpi, onClose }: KpiDetailV2Props) {
  const reduced = useMotionReduced();

  return (
    <motion.div
      className="glass-card"
      layoutId={`kpi-card-${kpi.id}`}
      variants={reduced ? undefined : containerTransform}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ padding: "2rem" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text)" }}>{kpi.name}</h2>
        <button
          onClick={onClose}
          style={{
            background: "var(--panel-2)",
            border: "1px solid var(--hair)",
            borderRadius: "var(--radius)",
            padding: "0.5rem 1rem",
            color: "var(--text)",
            cursor: "pointer",
          }}
        >
          Закрыть
        </button>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", marginBottom: "2rem" }}>
        <div style={{ fontSize: "3rem", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--text)" }}>
          {kpi.value.toLocaleString("ru-RU")}
        </div>
        <div style={{ fontSize: "1.25rem", color: "var(--muted)" }}>{kpi.unit}</div>
      </div>

      <div style={{ marginTop: "2rem", padding: "1rem", background: "var(--panel-2)", borderRadius: "var(--radius)" }}>
        <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
          Детали отклонения и причины будут подгружены через useSlice/useChain
        </p>
      </div>
    </motion.div>
  );
}