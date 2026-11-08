/** KpiCard — одна метрика KPI. Данные только из useDashboard (§10.2, T5.1). */
import type { KpiDTO, NodeStatus } from "../../api/types";
import { formatByn, formatPct } from "../../lib/format";
import { cn } from "../../lib/cn";

const STATUS_COLOR: Record<NodeStatus, string> = {
  red: "var(--alert)",
  yellow: "var(--warn)",
  green: "var(--ok)",
};

const STATUS_LABEL: Record<NodeStatus, string> = {
  red: "АЛЕРТ",
  yellow: "ВНИМАНИЕ",
  green: "НОРМА",
};

/** Форматирует значение метрики по её единице измерения. */
export function formatKpiValue(value: number, unit: string): string {
  if (unit === "%") return formatPct(value);
  if (unit === "BYN/сут") {
    return `${formatByn(value)}/сут`;
  }
  if (unit === "BYN/нед") {
    return `${formatByn(value)}/нед`;
  }
  const n = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 1 })
    .format(value)
    .replace(/[\u00A0\u202F]/g, " ");
  return unit ? `${n} ${unit}` : n;
}

interface KpiCardProps {
  kpi: KpiDTO;
}

export function KpiCard({ kpi }: KpiCardProps) {
  const color = STATUS_COLOR[kpi.status];
  return (
    <div className="card flex flex-col gap-1 p-3" style={{ minWidth: 0 }}>
      <div className="flex items-start justify-between gap-2">
        <p className="display text-xs leading-tight" style={{ color: "var(--muted)" }}>
          {kpi.name}
        </p>
        <span className={cn("tag shrink-0")} style={{ color }}>
          {STATUS_LABEL[kpi.status]}
        </span>
      </div>
      <p className="mono text-xl font-semibold truncate" style={{ color }}>
        {formatKpiValue(kpi.value, kpi.unit)}
      </p>
      {kpi.cost_per_day !== null && kpi.cost_per_day > 0 && (
        <p className="mono text-xs truncate" style={{ color: "var(--muted)" }}>
          {formatByn(kpi.cost_per_day)}/сут
        </p>
      )}
    </div>
  );
}