/**
 * TypeScript-зеркала Pydantic DTO из `backend/app/schemas.py` (§9 Readme.md).
 *
 * Правило: только типы, никакой логики и никаких экономических чисел.
 * Любое изменение бэкенд-схемы сначала делается в `schemas.py`, затем здесь.
 */

import type { MetricStatus, ScenarioId } from './dashboard';

// ──────────────────────────────────────────────────────────────────────
// What-If (§9.3)
// ──────────────────────────────────────────────────────────────────────

export interface WhatIfRequestDto {
  scenario: ScenarioId;
  node_id: string;
  value: number;
}

export interface WhatIfDeltaDto {
  d_downtime: number;
  d_sla: number;
  d_revenue: number;
  d_loss: number;
}

export interface RecommendedDto {
  type: 'hire';
  operators: number;
  expected_effect_byn: number;
  expected_defect_rate: number;
  expected_downtime_h: number;
}

export interface WhatIfDto {
  ops: number;
  downtime_h: number;
  sla_orders: number;
  revenue_week: number;
  loss_day: number;
  vs_now: WhatIfDeltaDto;
  recommended: RecommendedDto;
  chain_preview: string[];
}

// ──────────────────────────────────────────────────────────────────────
// Прогноз сезонности (§9.3)
// ──────────────────────────────────────────────────────────────────────

export interface ForecastDto {
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

// ──────────────────────────────────────────────────────────────────────
// Цепочка drill-down (§9.3)
// ──────────────────────────────────────────────────────────────────────

export interface ChainNodeDto {
  node_id: string;
  name: string;
  domain: string;
  value: number;
  unit: string;
  status: MetricStatus;
  cost_per_day: number | null;
  delta_from_parent: number | null;
}

export interface ChainDto {
  source: 'hint' | 'algorithm';
  chain: ChainNodeDto[];
}

// ──────────────────────────────────────────────────────────────────────
// Кросс-фильтр по дням (§9.3)
// ──────────────────────────────────────────────────────────────────────

export interface SliceFactDto {
  ts: string;
  domain: string;
  metric: string;
  value: number;
  dims: Record<string, string>;
}

export interface SliceDto {
  from: string;
  to: string;
  line: string | null;
  shift: number | null;
  facts: SliceFactDto[];
}

export interface SliceQuery {
  from: string;
  to: string;
  line?: string;
  shift?: number;
}

// ──────────────────────────────────────────────────────────────────────
// Юнит-экономика (§7.8, §9.3)
// ──────────────────────────────────────────────────────────────────────

export interface UnitEconDto {
  metric: string;
  unit: string;
  value: number;
  cost_per_unit: number;
  margin_byn: number;
  note: string | null;
}