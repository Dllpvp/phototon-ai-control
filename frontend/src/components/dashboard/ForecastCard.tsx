/** ForecastCard — превентивная карточка пика: заказы vs мощность, дефицит, простой, потери (§10.9, T5.5).
 *  Все числа — из ForecastDTO (GET /api/forecast), без хардкода.
 */
import type { UseQueryResult } from "@tanstack/react-query";

import type { ForecastDTO } from "../../api/types";
import { formatByn } from "../../lib/format";
import { AsyncState } from "./AsyncState";

interface ForecastCardProps {
  query: UseQueryResult<ForecastDTO, Error>;
  /** Открыть What-If с нужным числом операторов (§10.9: «Прогнать сценарий» → ops=6). */
  onRunScenario?: (ops: number) => void;
  /** Принять превентивное решение. */
  onAcceptPreventive?: () => void;
}

/** Операторы для «Прогнать сценарий» (§10.9). UI-константа, не экономический коэффициент. */
const FORECAST_SCENARIO_OPS = 6;

export function ForecastCard({ query, onRunScenario, onAcceptPreventive }: ForecastCardProps) {
  return (
    <AsyncState
      query={query}
      skeletonRows={3}
      isEmpty={(d) => !d}
      emptyText="Прогноз недоступен"
    >
      {(data) => {
        const shortfall = Math.max(0, data.deficit);
        return (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <span className="display text-lg font-semibold" style={{ color: "var(--text)" }}>
                Пик через 14 дней (неделя {data.week})
              </span>
              <span className="mono text-sm" style={{ color: "var(--muted)" }}>
                {data.forecast_orders} заказов при мощности {data.capacity_orders}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <div className="card flex flex-col gap-0.5 p-2">
                <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
                  дефицит, заказов
                </span>
                <span
                  className="mono text-lg font-semibold tabular-nums"
                  style={{ color: shortfall > 0 ? "var(--alert)" : "var(--ok)" }}
                >
                  {shortfall}
                </span>
              </div>

              <div className="card flex flex-col gap-0.5 p-2">
                <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
                  простой, ч/сут
                </span>
                <span className="mono text-lg font-semibold tabular-nums" style={{ color: "var(--warn)" }}>
                  {data.downtime_h.toFixed(1)}
                </span>
              </div>

              <div className="card flex flex-col gap-0.5 p-2">
                <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
                  потери, BYN/сут
                </span>
                <span className="mono text-lg font-semibold tabular-nums" style={{ color: "var(--alert)" }}>
                  {formatByn(data.loss_day)}
                </span>
              </div>

              <div className="card flex flex-col gap-0.5 p-2">
                <span className="mono text-[10px] uppercase" style={{ color: "var(--muted)" }}>
                  коэф. сезонности
                </span>
                <span className="mono text-lg font-semibold tabular-nums" style={{ color: "var(--text)" }}>
                  {data.seasonality_coeff.toFixed(2)}
                </span>
              </div>
            </div>

            {data.recommended_action && (
              <p className="memo text-sm" style={{ margin: 0 }}>
                Рекомендация: {data.recommended_action}
                {data.downtime_h_after !== null && data.loss_day_after !== null && (
                  <> · после решения: простой {data.downtime_h_after.toFixed(1)} ч/сут, потери {formatByn(data.loss_day_after)}/сут</>
                )}
              </p>
            )}

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="tag"
                style={{ color: "var(--accent)", cursor: "pointer" }}
                onClick={() => onRunScenario?.(FORECAST_SCENARIO_OPS)}
              >
                Прогнать сценарий
              </button>
              <button
                type="button"
                className="tag"
                style={{ color: "var(--text)", cursor: "pointer" }}
                onClick={() => onAcceptPreventive?.()}
              >
                Принять превентивное решение
              </button>
            </div>
          </div>
        );
      }}
    </AsyncState>
  );
}
