/** Зеркало всех DTO из `backend/app/schemas.py` (§9 Readme.md).
 *  Поля идентичны JSON-ответу; `GraphEdge.from` — алиас `from_` как в Pydantic.
 *  Строго типизировано, имена 1:1 как в Python.
 */

export type ScenarioId = "main" | "neg" | "peak";

export type Domain =
  | "finance"
  | "clients"
  | "production"
  | "hr"
  | "quality"
  | "season";

export type NodeStatus = "red" | "yellow" | "green";

export type EdgeSign = -1 | 1;

/** Общие DTO (§9.1) */
export interface Norm {
  lo: number | null;
  hi: number | null;
  unit: string;
  warn: number | null;
}

export interface GraphNode {
  id: string;
  domain: Domain;
  name: string;
  unit: string;
  value: number;
  norm: Norm | null;
  status: NodeStatus;
  cost_per_day: number | null;
  description: string | null;
  literal: boolean;
}

export interface GraphEdge {
  from: string;          // JSON key "from"
  to: string;
  sign: EdgeSign;
  weight: number;
  curvature: number | null;
  lag_days: number;
  note: string | null;
}

export interface Snapshot {
  scenario_id: ScenarioId;
  as_of: string;         // ISO date
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/** DTO для эндпоинтов (§9.3) */
export interface SliceDescDTO {
  week: number;
  line: string | null;
  shift: number | null;
}

export interface AlertDTO {
  node_id: string;
  title: string;
  delta_text: string;    // "−10 п.п."
  value_text: string;    // "32.0%"
  status: "red" | "yellow";
  cost_per_day: number;
  week: number;
  slice: SliceDescDTO;
}

export interface KpiDTO {
  node_id: string;
  domain: Domain;
  name: string;
  unit: string;
  value: number;
  status: NodeStatus;
  norm: Norm | null;
  cost_per_day: number | null;
}

export interface DashboardDTO {
  scenario_id: string;
  as_of: string;         // ISO date
  week: number;
  kpis: KpiDTO[];
  alerts: AlertDTO[];
  loss_counter_started_at: string;  // ISO datetime
  headline: string;
  updated_at: string;    // ISO datetime
}

export interface WhatIfDeltaDTO {
  d_downtime: number;
  d_sla: number;
  d_revenue: number;
  d_loss: number;
}

export interface RecommendedDTO {
  type: "hire";
  operators: number;
  expected_effect_byn: number;
  expected_defect_rate: number;
  expected_downtime_h: number;
}

export interface WhatIfDTO {
  ops: number;
  downtime_h: number;
  sla_orders: number;
  revenue_week: number;
  loss_day: number;
  vs_now: WhatIfDeltaDTO;
  recommended: RecommendedDTO;
  chain_preview: string[];
}

export interface ForecastDTO {
  week: number;
  seasonality_coeff: number;
  forecast_orders: number;
  capacity_orders: number;
  deficit: number;
  downtime_h: number;
  loss_day: number;
  recommended_action: string | null;
  downtime_h_after: number | null;
  loss_day_after: number | null;
}

export interface UnitEconDTO {
  sku: string;
  price: number;
  paper: number;
  printing: number;
  binding: number;
  labor: number;
  defect: number;
  margin_pct: number;
  status: "red" | "yellow" | "green";
}

export interface ChainNodeDTO {
  node_id: string;
  name: string;
  domain: string;
  value: number;
  unit: string;
  status: NodeStatus;
  cost_per_day: number | null;
  delta_from_parent: number | null;
}

export interface ChainDTO {
  source: "hint" | "algorithm";
  chain: ChainNodeDTO[];
}

export interface SliceFactDTO {
  ts: string;            // ISO date
  domain: string;
  metric: string;
  value: number;
  dims: Record<string, string>;
}

export interface SliceDTO {
  from: string;          // ISO date (JSON key "from")
  to: string;            // ISO date
  line: string | null;
  shift: number | null;
  facts: SliceFactDTO[];
}

export interface SimulationDTO {
  days: number;
  branch: "main" | "neg";
  effect_byn: number;
  verdict: "effective" | "ineffective";
  recommendation: string | null;
  compensating_cause: string | null;
  loss_day: number;
  defect_rate: number;
  downtime_h: number;
  final_snapshot: Record<string, { value: number; status: NodeStatus }>;
}

/** DTO для decisions, AI, notifications (§9.3 future) */
export interface DecisionDTO {
  id: string | null;
  scenario_id: string;
  type: "hire" | "maintenance" | "other";
  params: Record<string, number | string>;
  owner: string;
  due_date: string | null;     // ISO date
  expected_effect_byn: number;
  notes: string | null;
  baseline_snapshot: Record<string, number> | null;
  actual_effect_byn: number;
  verdict: "effective" | "ineffective" | "pending";
  created_at: string | null;   // ISO datetime
  jira_key: string | null;
  notification: NotificationDTO | null;
}

export interface AiDTO {
  scene: string;
  node_id: string;
  chain: string[];
  delta: Record<string, number>;
  cost_per_day: number;
  interpretation: string;
  source: "cache" | "deepseek" | "fallback";
  cache_hit: boolean;
}

export interface NotificationDTO {
  id: string;
  channel: "telegram" | "email" | "inapp";
  recipient: string;
  subject: string;
  body: string;
  status: "sent" | "failed" | "skipped_no_token";
  created_at: string;      // ISO datetime
  related_decision_id: string | null;
}

/** Request bodies */
export interface WhatIfRequest {
  scenario: ScenarioId;
  node_id: string;
  value: number;
}

export interface DecisionCreateRequest {
  scenario_id: string;
  type: "hire" | "maintenance" | "other";
  params: Record<string, number | string>;
  owner: string;
  due_date: string | null;
  expected_effect_byn: number;
  notes: string | null;
  baseline_snapshot: Record<string, number> | null;
}

export interface DecisionSimulateRequest {
  days: number;
  branch: "main" | "neg";
}

export interface AiInterpretRequest {
  scene: string;
  node_id: string;
  chain: string[];
  delta: Record<string, number>;
  cost_per_day: number;
}