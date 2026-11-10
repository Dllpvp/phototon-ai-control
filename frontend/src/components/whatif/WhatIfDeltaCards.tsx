/** WhatIfDeltaCards — 4 карточки дельт vs_now из WhatIfDTO (§10.4, T5.4). */
import type { WhatIfDeltaDTO } from "../../api/types";
import { formatByn } from "../../lib/format";

interface WhatIfDeltaCardsProps {
  delta: WhatIfDeltaDTO;
  isFact?: boolean;
}

function DeltaValue({ value, unit, invert }: { value: number; unit: string; invert?: boolean }) {
  const positive = invert ? value < 0 : value > 0;
  const zero = value === 0;
  const color = zero ? "var(--muted)" : positive ? "var(--ok)" : "var(--alert)";
  const sign = value > 0 ? "+" : "";
  const formatted = unit === "BYN" ? formatByn(value) : `${sign}${value} ${unit}`;
  return (
    <span className="mono text-lg font-semibold tabular-nums" style={{ color }}>
      {zero ? "0" : formatted}
    </span>
  );
}

export function WhatIfDeltaCards({ delta, isFact = false }: WhatIfDeltaCardsProps) {
  const displayedDelta = isFact
    ? { d_downtime: 0, d_sla: 0, d_revenue: 0, d_loss: 0 }
    : delta;
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      <div className="card flex flex-col gap-0.5 p-2">
        <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
          простои, ч
        </span>
        <DeltaValue value={displayedDelta.d_downtime} unit="ч" invert />
      </div>
      <div className="card flex flex-col gap-0.5 p-2">
        <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
          SLA-просв., зак.
        </span>
        <DeltaValue value={displayedDelta.d_sla} unit="зак." invert />
      </div>
      <div className="card flex flex-col gap-0.5 p-2">
        <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
          выручка, нед
        </span>
        <DeltaValue value={displayedDelta.d_revenue} unit="BYN" />
      </div>
      <div className="card flex flex-col gap-0.5 p-2">
        <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
          потери, сут
        </span>
        <DeltaValue value={displayedDelta.d_loss} unit="BYN" invert />
      </div>
    </div>
  );
}
