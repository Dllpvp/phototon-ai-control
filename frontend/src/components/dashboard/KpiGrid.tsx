/** KpiGrid — сетка KPI-карточек. Данные только из useDashboard (§10.2, T5.1). */
import type { UseQueryResult } from "@tanstack/react-query";

import type { DashboardDTO } from "../../api/types";
import { AsyncState } from "./AsyncState";
import { KpiCard } from "./KpiCard";

interface KpiGridProps {
  query: UseQueryResult<DashboardDTO, Error>;
}

export function KpiGrid({ query }: KpiGridProps) {
  return (
    <AsyncState
      query={query}
      skeletonRows={4}
      isEmpty={(d) => d.kpis.length === 0}
      emptyText="KPI недоступны"
    >
      {(data) => (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {data.kpis.map((kpi) => (
            <KpiCard key={kpi.node_id} kpi={kpi} />
          ))}
        </div>
      )}
    </AsyncState>
  );
}
