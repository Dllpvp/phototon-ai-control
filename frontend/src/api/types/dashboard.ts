/**
 * TypeScript-зеркала Pydantic DTO из `backend/app/schemas.py` (§9 Readme.md).
 *
 * Правило: только типы, никакой логики и никаких экономических чисел.
 * Любое изменение бэкенд-схемы сначала делается в `schemas.py`, затем здесь.
 */

// ──────────────────────────────────────────────────────────────────────
// Общие DTO (§9.1)
// ──────────────────────────────────────────────────────────────────────

export type Domain = 'finance' | 'clients' | 'production' | 'hr' | 'quality' | 'season';

export type MetricStatus = 'red' | 'yellow' | 'green';

export type ScenarioId = 'main' | 'neg' | 'peak';

export interface NormDto {
  lo: number | null;
  hi: number | null;
  unit: string;
}

export interface GraphNodeDto {
  id: string;
  domain: Domain;
  name: string;
  unit: string;
  value: number;
  norm: NormDto | null;
  status: MetricStatus;
  cost_per_day: number | null;
  description: string | null;
  literal: boolean;
}

/** Ребро графа: на бэкенде поле `from_` сериализуется как `from`. */
export interface GraphEdgeDto {
  from: string;
  to: string;
  sign: -1 | 1;
  weight: number;
  curvature: number | null;
  lag_days: number;
  note: string | null;
}

export interface SnapshotDto {
  scenario_id: ScenarioId;
  as_of: string;
  nodes: GraphNodeDto[];
  edges: GraphEdgeDto[];
}

// ──────────────────────────────────────────────────────────────────────
// Дашборд (§9.3)
// ──────────────────────────────────────────────────────────────────────

export interface SliceDescDto {
  week: number;
  line: string | null;
  shift: number | null;
}

export interface AlertDto {
  node_id: string;
  title: string;
  delta_text: string;
  value_text: string;
  status: 'red' | 'yellow';
  cost_per_day: number;
  week: number;
  slice: SliceDescDto;
}

export interface KpiDto {
  node_id: string;
  domain: Domain;
  name: string;
  unit: string;
  value: number;
  status: MetricStatus;
  norm: NormDto | null;
  cost_per_day: number | null;
}

export interface DashboardDto {
  scenario_id: string;
  as_of: string;
  week: number;
  kpis: KpiDto[];
  alerts: AlertDto[];
  loss_counter_started_at: string;
  headline: string;
  updated_at: string;
}