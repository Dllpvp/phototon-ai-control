/** WhatIfTable — 3-строковая таблица anchors (4/5/6 операторов) с подсветкой текущей строки (§10.4, T5.4).
 *  Значения приходят из API (useWhatIf для каждого ops), не хардкодятся.
 */
import type { WhatIfDTO } from "../../api/types";
import { formatByn } from "../../lib/format";

interface WhatIfTableProps {
  rows: { ops: number; data: WhatIfDTO }[];
  currentOps: number;
}

export function WhatIfTable({ rows, currentOps }: WhatIfTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[10px] sm:text-xs mono" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--hair-strong)" }}>
            <th className="p-1.5 text-left font-semibold" style={{ color: "var(--muted)" }}>Операторов</th>
            <th className="p-1.5 text-right font-semibold" style={{ color: "var(--muted)" }}>Простои, ч</th>
            <th className="p-1.5 text-right font-semibold" style={{ color: "var(--muted)" }}>SLA-просв.</th>
            <th className="p-1.5 text-right font-semibold" style={{ color: "var(--muted)" }}>Выручка/нед</th>
            <th className="p-1.5 text-right font-semibold" style={{ color: "var(--muted)" }}>Потери/сут</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ ops, data }) => {
            const active = ops === currentOps;
            return (
              <tr
                key={ops}
                style={{
                  borderBottom: "1px solid var(--hair)",
                  background: active ? "var(--panel-2)" : "transparent",
                  fontWeight: active ? 600 : 400,
                }}
              >
                <td className="p-1.5" style={{ color: active ? "var(--accent)" : "var(--text)" }}>
                  {ops}
                  {active && <span className="ml-1" style={{ color: "var(--muted)" }}>← сейчас</span>}
                </td>
                <td className="p-1.5 text-right tabular-nums">{data.downtime_h.toFixed(1)}</td>
                <td className="p-1.5 text-right tabular-nums">{data.sla_orders}</td>
                <td className="p-1.5 text-right tabular-nums">{formatByn(data.revenue_week)}</td>
                <td
                  className="p-1.5 text-right tabular-nums"
                  style={{ color: data.loss_day > 1000 ? "var(--alert)" : "var(--ok)" }}
                >
                  {formatByn(data.loss_day)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
