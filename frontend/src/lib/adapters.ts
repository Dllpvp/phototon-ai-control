/** Адаптеры для преобразования DTO в UI-типы. */
import type { KpiDTO } from "../api/types";

/** KPI-карточка для отображения в сетке. */
export interface KpiData {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "red" | "yellow" | "green";
  periods?: { period: string; value: number }[];
}

/** Преобразует KpiDTO в KpiData для UI. */
export function adaptKpi(kpi: KpiDTO): KpiData {
  return {
    id: kpi.node_id,
    name: kpi.name,
    value: kpi.value,
    unit: kpi.unit,
    status: kpi.status === "hidden" ? "green" : kpi.status,
    periods: undefined,
  };
}