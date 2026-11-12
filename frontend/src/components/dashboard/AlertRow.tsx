/** AlertRow — одна строка алерта. Порядок и сортировка приходят с API, во фронте не сортируем
 *  (§10.2, T5.1). Клик → выбор узла в UI-сторе (раскрывает цепочку).
 */
import type { AlertDTO } from "../../api/types";
import { formatByn } from "../../lib/format";

const STATUS_COLOR: Record<AlertDTO["status"], string> = {
  red: "var(--alert)",
  yellow: "var(--warn)",
};

interface AlertRowProps {
  alert: AlertDTO;
  /** Выбор узла для раскрытия цепочки (store.ui.selectNode). */
  onSelect: (nodeId: string) => void;
}

export function AlertRow({ alert, onSelect }: AlertRowProps) {
  const color = STATUS_COLOR[alert.status];
  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(alert.node_id)}
        className="card flex w-full flex-col gap-1 p-2 text-left"
        style={{ minWidth: 0, cursor: "pointer" }}
      >
        <div className="flex items-center gap-2" style={{ minWidth: 0 }}>
          <span className="live-dot shrink-0" style={{ background: color }} />
          <span className="display truncate text-sm" style={{ color: "var(--text)" }}>
            {alert.title}
          </span>
        </div>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 mono text-xs">
          <span style={{ color }}>{alert.delta_text}</span>
          <span style={{ color: "var(--muted)" }}>{alert.value_text}</span>
          {alert.cost_per_day > 0 && (
            <span className="ml-auto shrink-0" style={{ color: "var(--muted)" }}>
              {formatByn(alert.cost_per_day)}/сут
            </span>
          )}
        </div>
      </button>
    </li>
  );
}
