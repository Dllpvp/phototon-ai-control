/** WhatIfSlider — ползунок операторов смены №3 + таблица anchors + дельты + кнопка «Принять как решение» (§10.4, T5.4).
 *  Debounce 120 мс на отпускании ползунка. Таблица 4/5/6 запрашивается отдельными what-if вызовами.
 */
import { useCallback, useEffect, useRef, useState } from "react";

import { useWhatIf } from "../../api/queries";
import type { WhatIfDTO, WhatIfRequest } from "../../api/types";
import { useDemoStore } from "../../store/demo";
import { useUIStore } from "../../store/ui";
import { formatByn } from "../../lib/format";
import { WhatIfDeltaCards } from "./WhatIfDeltaCards";
import { WhatIfTable } from "./WhatIfTable";

const OPS_VALUES = [4, 5, 6] as const;
const DEBOUNCE_MS = 120;

interface WhatIfSliderProps {
  /** Прокрутка к форме решения после нажатия «Принять как решение». */
  onAccept?: () => void;
}

export function WhatIfSlider({ onAccept }: WhatIfSliderProps) {
  const scenario = useUIStore((s) => s.scenario);
  const setPrefilledDecision = useDemoStore((s) => s.setPrefilledDecision);

  const [ops, setOps] = useState<number>(4);
  const [debouncedOps, setDebouncedOps] = useState<number>(4);
  const timerRef = useRef<number | null>(null);

  const whatIf = useWhatIf();

  // Debounce: обновляем debouncedOps через 120 мс после последнего изменения
  useEffect(() => {
    if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => setDebouncedOps(ops), DEBOUNCE_MS);
    return () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    };
  }, [ops]);

  // Запрос what-if при смене debouncedOps
  useEffect(() => {
    const body: WhatIfRequest = { scenario, node_id: "hr_operators_s3", value: debouncedOps };
    whatIf.mutate(body);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedOps, scenario]);

  // Запросы для таблицы (все 3 значения) — выполняем один раз при монтировании
  const [tableRows, setTableRows] = useState<{ ops: number; data: WhatIfDTO }[]>([]);
  const tableFetchedRef = useRef(false);

  useEffect(() => {
    if (tableFetchedRef.current) return;
    tableFetchedRef.current = true;
    const rows: { ops: number; data: WhatIfDTO }[] = [];
    let pending = OPS_VALUES.length;
    OPS_VALUES.forEach((v) => {
      const body: WhatIfRequest = { scenario, node_id: "hr_operators_s3", value: v };
      whatIf.mutate(body, {
        onSuccess: (data) => {
          rows.push({ ops: v, data });
          rows.sort((a, b) => a.ops - b.ops);
          pending -= 1;
          if (pending === 0) setTableRows([...rows]);
        },
      });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scenario]);

  const current = whatIf.data;

  const handleAccept = useCallback(() => {
    const addOps = Math.max(0, Math.round(debouncedOps - 4));
    setPrefilledDecision({ type: "hire", params: { operators: addOps, shift: 3 } });
    onAccept?.();
  }, [debouncedOps, setPrefilledDecision, onAccept]);

  return (
    <div className="card flex flex-col gap-3 p-3">
      <div className="flex items-center justify-between">
        <span className="display text-sm font-semibold">What-If: операторы смены №3</span>
        <span className="mono text-lg font-bold tabular-nums" style={{ color: "var(--accent)" }}>
          {ops}
        </span>
      </div>

      <input
        type="range"
        className="slider"
        min={4}
        max={6}
        step={0.5}
        value={ops}
        onChange={(e) => setOps(Number(e.target.value))}
        aria-label="Количество операторов смены №3"
      />

      <div className="flex justify-between mono text-[10px]" style={{ color: "var(--muted)" }}>
        <span>4 (факт)</span>
        <span>5</span>
        <span>6</span>
      </div>

      {current && <WhatIfDeltaCards delta={current.vs_now} />}

      {tableRows.length === OPS_VALUES.length && (
        <WhatIfTable rows={tableRows} currentOps={debouncedOps} />
      )}

      {current && (
        <div className="flex flex-col gap-1.5 border-t pt-2" style={{ borderColor: "var(--hair)" }}>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mono text-xs">
            <span style={{ color: "var(--muted)" }}>
              Рекомендация: нанять <strong style={{ color: "var(--text)" }}>{current.recommended.operators}</strong> операторов
            </span>
            <span style={{ color: "var(--muted)" }}>
              Эффект: <strong style={{ color: "var(--ok)" }}>{formatByn(current.recommended.expected_effect_byn)}</strong> за 14 дней
            </span>
          </div>
          <button
            type="button"
            className="tag self-start"
            style={{ color: "var(--accent)", borderColor: "var(--accent)" }}
            onClick={handleAccept}
          >
            Принять как решение
          </button>
        </div>
      )}

      {whatIf.isPending && (
        <div className="mono text-xs" style={{ color: "var(--muted)" }}>Расчёт…</div>
      )}
      {whatIf.isError && (
        <div className="mono text-xs" style={{ color: "var(--alert)" }}>
          Ошибка расчёта: {whatIf.error.message}
        </div>
      )}
    </div>
  );
}
