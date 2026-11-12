/** TanStack Query-хуки + queryKeys-фабрика (§9, T4.1, T9g: role/dept в ключах). */
import { useMutation, useQuery, type UseMutationResult, type UseQueryResult } from "@tanstack/react-query";

import { useDemoStore } from "../store/demo";
import { getJson, postJson } from "./client";
import type {
  AiDTO,
  AiInterpretRequest,
  AuditDTO,
  ChainDTO,
  DashboardDTO,
  DecisionCreateRequest,
  DecisionDTO,
  DecisionSimulateRequest,
  DemoDept,
  DemoRole,
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

/**
 * Роль+отдел демо-RBAC. Входит во все роле-зависимые queryKey,
 * чтобы смена роли не отдавала кэш другой роли (T9g, спека п.4).
 */
export function useRoleScope(): readonly [DemoRole, DemoDept | null] {
  const role = useDemoStore((s) => s.role);
  const dept = useDemoStore((s) => s.dept);
  return [role, dept] as const;
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
  audit: () => ["security", "audit"] as const,
} as const;

export function useSnapshot(scenario: string): UseQueryResult<Snapshot, Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.snapshot(scenario), ...scope],
    queryFn: () => getJson<Snapshot>(`/api/snapshot${qs({ scenario })}`),
  });
}

export function useDashboard(scenario: string): UseQueryResult<DashboardDTO, Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.dashboard(scenario), ...scope],
    queryFn: () => getJson<DashboardDTO>(`/api/dashboard${qs({ scenario })}`),
    refetchInterval: 30_000,
  });
}

export function useChain(nodeId: string | null): UseQueryResult<ChainDTO, Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.chain(nodeId), ...scope],
    queryFn: () => getJson<ChainDTO>(`/api/chain/${encodeURIComponent(nodeId as string)}`),
    enabled: nodeId !== null,
  });
}

export function useSlice(params: SliceParams | null): UseQueryResult<SliceDTO, Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.slice(params), ...scope],
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
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.forecast(scenario), ...scope],
    queryFn: () => getJson<ForecastDTO>(`/api/forecast${qs({ scenario })}`),
  });
}

export function useUnitEcon(): UseQueryResult<UnitEconDTO[], Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.unitEcon(), ...scope],
    queryFn: () => getJson<UnitEconDTO[]>("/api/unit-economics"),
  });
}

export function useDecisions(scenario?: string): UseQueryResult<DecisionDTO[], Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.decisions(scenario), ...scope],
    queryFn: () =>
      getJson<DecisionDTO[]>(`/api/decisions${scenario ? qs({ scenario_id: scenario }) : ""}`),
  });
}

export function useNotifications(): UseQueryResult<NotificationDTO[], Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.notifications(), ...scope],
    queryFn: () => getJson<NotificationDTO[]>("/api/notifications"),
  });
}

/** Журнал аудита вызовов LLM. Только для роли director (иначе backend вернёт 403). */
export function useSecurityAudit(last: number): UseQueryResult<AuditDTO[], Error> {
  const scope = useRoleScope();
  return useQuery({
    queryKey: [...queryKeys.audit(), last, ...scope],
    queryFn: () => getJson<AuditDTO[]>(`/api/security/audit${qs({ last })}`),
    retry: false,
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
