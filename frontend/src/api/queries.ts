/** TanStack Query-хуки + queryKeys-фабрика (§9, T4.1). */
import { useMutation, useQuery, type UseMutationResult, type UseQueryResult } from "@tanstack/react-query";

import { getJson, postJson } from "./client";
import type {
  AiDTO,
  AiInterpretRequest,
  ChainDTO,
  DashboardDTO,
  DecisionCreateRequest,
  DecisionDTO,
  DecisionSimulateRequest,
  ForecastDTO,
  NotificationDTO,
  SliceDTO,
  SimulationDTO,
  Snapshot,
  UnitEconDTO,
  WhatIfDTO,
  WhatIfRequest,
} from "./types";

export interface SliceParams {
  from: string;
  to: string;
  line?: string;
  shift?: number;
}

function qs(params: Record<string, string | number | undefined>): string {
  const s = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== "")
    .map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`)
    .join("&");
  return s ? `?${s}` : "";
}

export const queryKeys = {
  snapshot: (scenario: string) => ["snapshot", scenario] as const,
  dashboard: (scenario: string) => ["dashboard", scenario] as const,
  chain: (nodeId: string | null) => ["chain", nodeId] as const,
  slice: (p: SliceParams | null) => ["slice", p] as const,
  whatif: () => ["whatif"] as const,
  forecast: (scenario: string) => ["forecast", scenario] as const,
  unitEcon: () => ["unit-econ"] as const,
  decisions: (scenario?: string) => ["decisions", scenario ?? null] as const,
  notifications: () => ["notifications"] as const,
  decision: (id: string) => ["decision", id] as const,
  ai: () => ["ai"] as const,
} as const;

export function useSnapshot(scenario: string): UseQueryResult<Snapshot, Error> {
  return useQuery({
    queryKey: queryKeys.snapshot(scenario),
    queryFn: () => getJson<Snapshot>(`/api/snapshot${qs({ scenario })}`),
  });
}

export function useDashboard(scenario: string): UseQueryResult<DashboardDTO, Error> {
  return useQuery({
    queryKey: queryKeys.dashboard(scenario),
    queryFn: () => getJson<DashboardDTO>(`/api/dashboard${qs({ scenario })}`),
    refetchInterval: 30_000,
  });
}

export function useChain(nodeId: string | null): UseQueryResult<ChainDTO, Error> {
  return useQuery({
    queryKey: queryKeys.chain(nodeId),
    queryFn: () => getJson<ChainDTO>(`/api/chain/${encodeURIComponent(nodeId as string)}`),
    enabled: nodeId !== null,
  });
}

export function useSlice(params: SliceParams | null): UseQueryResult<SliceDTO, Error> {
  return useQuery({
    queryKey: queryKeys.slice(params),
    queryFn: () =>
      getJson<SliceDTO>(
        `/api/slice${qs({
          from: params?.from,
          to: params?.to,
          line: params?.line,
          shift: params?.shift,
        })}`,
      ),
    enabled: params !== null,
  });
}

export function useWhatIf(): UseMutationResult<WhatIfDTO, Error, WhatIfRequest> {
  return useMutation({
    mutationKey: ["whatif"],
    mutationFn: (body: WhatIfRequest) => postJson<WhatIfDTO>("/api/whatif", body),
  });
}

export function useForecast(scenario: string): UseQueryResult<ForecastDTO, Error> {
  return useQuery({
    queryKey: queryKeys.forecast(scenario),
    queryFn: () => getJson<ForecastDTO>(`/api/forecast${qs({ scenario })}`),
  });
}

export function useUnitEcon(): UseQueryResult<UnitEconDTO[], Error> {
  return useQuery({
    queryKey: queryKeys.unitEcon(),
    queryFn: () => getJson<UnitEconDTO[]>("/api/unit-economics"),
  });
}

export function useDecisions(scenario?: string): UseQueryResult<DecisionDTO[], Error> {
  return useQuery({
    queryKey: queryKeys.decisions(scenario),
    queryFn: () =>
      getJson<DecisionDTO[]>(`/api/decisions${scenario ? qs({ scenario_id: scenario }) : ""}`),
  });
}

export function useNotifications(): UseQueryResult<NotificationDTO[], Error> {
  return useQuery({
    queryKey: queryKeys.notifications(),
    queryFn: () => getJson<NotificationDTO[]>("/api/notifications"),
  });
}

export function useCreateDecision(): UseMutationResult<DecisionDTO, Error, DecisionCreateRequest> {
  return useMutation({
    mutationKey: ["decisions", "create"],
    mutationFn: (body: DecisionCreateRequest) => postJson<DecisionDTO>("/api/decisions", body),
  });
}

export function useSimulate(): UseMutationResult<
  SimulationDTO,
  Error,
  { id: string; params: DecisionSimulateRequest }
> {
  return useMutation({
    mutationKey: ["decisions", "simulate"],
    mutationFn: ({ id, params }) =>
      postJson<SimulationDTO>(`/api/decisions/${encodeURIComponent(id)}/simulate`, params),
  });
}

export function useAi(): UseMutationResult<AiDTO, Error, AiInterpretRequest> {
  return useMutation({
    mutationKey: ["ai"],
    mutationFn: (body: AiInterpretRequest) => postJson<AiDTO>("/api/ai/interpret", body),
  });
}