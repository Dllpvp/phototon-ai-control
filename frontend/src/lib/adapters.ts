/**
 * Адаптеры DTO → view-model.
 * Маппят реальные поля API на типы, которые используют компоненты.
 * Все "отсутствующие" поля — optional, без фейковых значений.
 */

import type {
  AlertDTO,
  ChainDTO,
  ChainNodeDTO,
  DecisionDTO,
  KpiDTO,
} from "../api/types";

// ===== VIEW-MODEL ТИПЫ =====

export interface KpiData {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "red" | "yellow" | "green";
  costPerDay: number | null;
  domain: string;
  /** Опционально: периоды загружаются через useSlice при раскрытии */
  periods?: { period: string; value: number }[];
}

export interface TableKpi {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "red" | "yellow" | "green";
  /** Опционально: тренд загружается по требованию */
  trend?: number[];
  /** Опционально: причины загружаются через useChain по клику */
  causes?: ChainCause[];
}

export interface ChainCause {
  id: string;
  name: string;
  value: number;
  unit: string;
  domain: string;
  deltaFromParent: number | null;
}

export interface DecisionAlert {
  id: string;
  kpiName: string;
  description: string;
  status: "red" | "yellow";
  costPerDay: number;
  week: number;
  slice: {
    week: number;
    line: string | null;
    shift: number | null;
  };
}

export type DecisionRecordStatus = "effective" | "ineffective" | "pending";

export interface DecisionRecord {
  id: string;
  jiraKey: string | null;
  action: string;
  responsible: string;
  deadline: string | null;
  status: DecisionRecordStatus;
  expectedEffect: number;
  actualEffect: number;
  createdAt: string | null;
}

export interface WhyDeviationCause {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "red" | "yellow" | "green";
  deltaFromParent: number | null;
}

export interface WhyDeviationVM {
  fact: number | undefined;
  unit: string | undefined;
  plan: number | undefined;
  causes: WhyDeviationCause[];
}

// ===== МАППЕРЫ =====

export function toKpiData(k: KpiDTO): KpiData {
  return {
    id: k.node_id,
    name: k.name,
    value: k.value,
    unit: k.unit,
    status: k.status,
    costPerDay: k.cost_per_day,
    domain: k.domain,
    // periods не мапим — загружается через useSlice при раскрытии
  };
}

export function toTableKpi(k: KpiDTO): TableKpi {
  return {
    id: k.node_id,
    name: k.name,
    value: k.value,
    unit: k.unit,
    status: k.status,
    // trend и causes не мапим — загружаются по требованию
  };
}

export function toDecisionAlert(a: AlertDTO): DecisionAlert {
  return {
    id: a.node_id,
    kpiName: a.title,
    description: `${a.delta_text} · ${a.value_text}`,
    status: a.status,
    costPerDay: a.cost_per_day,
    week: a.week,
    slice: a.slice,
  };
}

export function toDecisionRecord(d: DecisionDTO): DecisionRecord {
  // Формируем читаемое действие из type + params
  const actionParts = [d.type];
  if (d.params && Object.keys(d.params).length > 0) {
    const paramsStr = Object.entries(d.params)
      .map(([k, v]) => `${k}=${v}`)
      .join(", ");
    actionParts.push(`(${paramsStr})`);
  }

  return {
    id: d.id ?? "unknown",
    jiraKey: d.jira_key,
    action: actionParts.join(" "),
    responsible: d.owner,
    deadline: d.due_date,
    status: d.verdict ?? "pending",
    expectedEffect: d.expected_effect_byn,
    actualEffect: d.actual_effect_byn,
    createdAt: d.created_at,
  };
}

/**
 * Маппинг ChainDTO → WhyDeviationVM.
 * Первый узел = факт, его норма = план, остальные = причины.
 */
export function toWhyDeviation(c: ChainDTO | undefined): WhyDeviationVM {
  if (!c || c.chain.length === 0) {
    return { fact: undefined, unit: undefined, plan: undefined, causes: [] };
  }

  const [head, ...rest] = c.chain;
  const plan = head.norm?.hi ?? head.norm?.lo;

  const causes: WhyDeviationCause[] = rest.map((n: ChainNodeDTO) => ({
    id: n.node_id,
    name: n.name,
    value: n.value,
    unit: n.unit,
    status: n.status,
    deltaFromParent: n.delta_from_parent,
  }));

  return {
    fact: head.value,
    unit: head.unit,
    plan,
    causes,
  };
}

/**
 * Маппинг ChainNodeDTO → ChainCause (для IndicatorsTable).
 */
export function toChainCause(n: ChainNodeDTO): ChainCause {
  return {
    id: n.node_id,
    name: n.name,
    value: n.value,
    unit: n.unit,
    domain: n.domain,
    deltaFromParent: n.delta_from_parent,
  };
}