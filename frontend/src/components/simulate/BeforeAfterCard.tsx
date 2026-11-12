/** BeforeAfterCard — «было → стало» по SimulationDTO (§10.7, T6.4).
 *  «Было» берётся из decision.baseline_snapshot, иначе из fallbackSnapshot.nodes.
 *  «Стало» — из simulation.final_snapshot. Все числа — из DTO, без литералов.
 */
import type { DecisionDTO, NodeStatus, SimulationDTO, Snapshot } from "../../api/types";
import { formatByn, formatPct } from "../../lib/format";

const MAX_ROWS = 5;

const STATUS_COLOR: Record<NodeStatus, string> = {
  red: "var(--alert)",
  yellow: "var(--warn)",
  green: "var(--ok)",
  hidden: "var(--muted)",
};

function getNodeColor(entry: { status?: NodeStatus }): string {
  if (entry.status && STATUS_COLOR[entry.status]) return STATUS_COLOR[entry.status];
  return "var(--muted)";
}

export interface BeforeAfterCardProps {
  /** Решение: из него берётся baseline, если он сохранён. */
  decision: DecisionDTO | null;
  /** Результат симуляции; без него карточка ничего не выдумывает. */
  simulation: SimulationDTO | null;
  /** Статичный снимок сценария — фолбэк для «было» и словарь имён/единиц. */
  fallbackSnapshot?: Snapshot | null;
  /** Кнопка «А если бы не сработало?» → негативная ветка (§10.8). */
  onNegative?: () => void;
}

interface ChangedRow {
  nodeId: string;
  label: string;
  unit: string;
  before: number;
  after: number;
  status: NodeStatus;
}

function buildBefore(
  decision: DecisionDTO | null,
  fallbackSnapshot: Snapshot | null | undefined,
): Record<string, number> {
  if (decision?.baseline_snapshot) return decision.baseline_snapshot;
  const out: Record<string, number> = {};
  for (const node of fallbackSnapshot?.nodes ?? []) {
    if (node.value !== null) out[node.id] = node.value;
  }
  return out;
}

function nodeMeta(
  nodeId: string,
  fallbackSnapshot: Snapshot | null | undefined,
): { name: string; unit: string } {
  const node = fallbackSnapshot?.nodes.find((item) => item.id === nodeId);
  return { name: node?.name ?? nodeId, unit: node?.unit ?? "" };
}

function formatValue(value: number, unit: string): string {
  if (unit === "%") return formatPct(value);
  if (unit === "BYN") return formatByn(value);
  if (unit === "ч") return `${new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 1 }).format(value)} ч`;
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(value);
}

function changedRows(
  before: Record<string, number>,
  simulation: SimulationDTO,
  fallbackSnapshot: Snapshot | null | undefined,
): ChangedRow[] {
  const rows: ChangedRow[] = [];
  for (const [nodeId, entry] of Object.entries(simulation.final_snapshot)) {
    const previous = before[nodeId];
    if (previous === undefined || previous === entry.value) continue;
    const meta = nodeMeta(nodeId, fallbackSnapshot);
    rows.push({
      nodeId,
      label: meta.name,
      unit: meta.unit,
      before: previous,
      after: entry.value,
      status: entry.status,
    });
  }
  rows.sort((a, b) => Math.abs(b.after - b.before) - Math.abs(a.after - a.before));
  return rows.slice(0, MAX_ROWS);
}

export function BeforeAfterCard({
  decision,
  simulation,
  fallbackSnapshot,
  onNegative,
}: BeforeAfterCardProps) {
  if (!simulation) {
    return (
      <p className="mono text-sm" style={{ color: "var(--muted)" }}>
        Нет данных симуляции.
      </p>
    );
  }

  const before = buildBefore(decision, fallbackSnapshot);
  const rows = changedRows(before, simulation, fallbackSnapshot);
  const effective = simulation.verdict === "effective";
  const sign = simulation.effect_byn >= 0 ? "+" : "−";

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="display text-lg font-semibold" style={{ color: "var(--text)" }}>
          Эффект решения: {sign}
          {formatByn(Math.abs(simulation.effect_byn))}
        </span>
        <span className="mono text-xs" style={{ color: "var(--muted)" }}>
          за {simulation.days} дн.
        </span>
        <span className="tag" style={{ color: effective ? "var(--ok)" : "var(--alert)" }}>
          {effective ? "ЭФФЕКТИВНО" : "НЕЭФФЕКТИВНО"}
        </span>
      </div>

      <table className="w-full mono text-sm" style={{ color: "var(--text)" }}>
        <thead>
          <tr style={{ color: "var(--muted)" }}>
            <th className="text-left font-normal">Показатель</th>
            <th className="text-right font-normal">Было</th>
            <th className="text-right font-normal">Стало</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={3} style={{ color: "var(--muted)" }}>
                Значимых изменений нет.
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.nodeId} title={row.nodeId}>
                <td className="text-left">{row.label}</td>
                <td className="text-right">{formatValue(row.before, row.unit)}</td>
                <td className="text-right" style={{ color: getNodeColor({ status: row.status }) }}>
                  {formatValue(row.after, row.unit)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      <div className="flex flex-wrap gap-x-4 gap-y-1 mono text-sm" style={{ color: "var(--text)" }}>
        <span>Потери: {formatByn(simulation.loss_day)}/сут</span>
        <span>Брак: {formatPct(simulation.defect_rate)}</span>
        <span>Простой: {new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 1 }).format(simulation.downtime_h)} ч</span>
      </div>

      {onNegative && (
        <button
          type="button"
          className="tag self-start"
          style={{ color: "var(--accent)", cursor: "pointer" }}
          onClick={onNegative}
        >
          А если бы не сработало?
        </button>
      )}
    </div>
  );
}