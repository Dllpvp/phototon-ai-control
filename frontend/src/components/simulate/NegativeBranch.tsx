/** Негативная ветка симуляции (§10.8). Все показатели читаются из DTO. */
import type { SimulationDTO, Snapshot } from "../../api/types";
import { formatByn, formatPct } from "../../lib/format";

interface NegativeBranchProps {
  simulation: SimulationDTO;
  snapshot?: Snapshot | null;
  onMaintenance: () => void;
}

function causeLabel(simulation: SimulationDTO, snapshot: Snapshot | null | undefined): string {
  const cause = simulation.compensating_cause;
  if (!cause) return "—";
  return snapshot?.nodes.find((node) => node.id === cause)?.name ?? cause;
}

export function NegativeBranch({ simulation, snapshot, onMaintenance }: NegativeBranchProps) {
  const wear = simulation.compensating_cause
    ? simulation.final_snapshot[simulation.compensating_cause]?.value
    : undefined;
  const downtime = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 1 }).format(simulation.downtime_h);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-x-4 gap-y-1 mono text-sm" style={{ color: "var(--text)" }}>
        <span>Потери: {formatByn(simulation.loss_day)}/сут</span>
        <span>Брак: {formatPct(simulation.defect_rate)}</span>
        <span>Простой: {downtime} ч</span>
      </div>
      <p className="memo serif text-sm" style={{ color: "var(--muted)" }}>
        Компенсирующая причина: {causeLabel(simulation, snapshot)}
        {wear === undefined ? "" : ` (${formatPct(wear)}).`}
        {simulation.recommendation ? ` Рекомендация: ${simulation.recommendation}` : ""}
      </p>
      <button type="button" className="tag self-start" style={{ color: "var(--accent)", cursor: "pointer" }} onClick={onMaintenance}>
        Оформить ТО
      </button>
    </div>
  );
}
