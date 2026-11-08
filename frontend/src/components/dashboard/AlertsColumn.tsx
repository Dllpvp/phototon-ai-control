/** AlertsColumn — список алертов. Порядок приходит с API (§10.2, T5.1). */
import type { UseQueryResult } from "@tanstack/react-query";

import type { DashboardDTO } from "../../api/types";
import { AsyncState } from "./AsyncState";
import { AlertRow } from "./AlertRow";

interface AlertsColumnProps {
  query: UseQueryResult<DashboardDTO, Error>;
  onSelect: (nodeId: string) => void;
}

export function AlertsColumn({ query, onSelect }: AlertsColumnProps) {
  return (
    <AsyncState
      query={query}
      skeletonRows={3}
      isEmpty={(d) => d.alerts.length === 0}
      emptyText="Алертов нет — все метрики в норме"
    >
      {(data) => (
        <ul className="flex flex-col gap-2">
          {data.alerts.map((alert) => (
            <AlertRow key={alert.node_id} alert={alert} onSelect={onSelect} />
          ))}
        </ul>
      )}
    </AsyncState>
  );
}
