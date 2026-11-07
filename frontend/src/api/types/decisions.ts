/**
 * TypeScript-зеркала DTO решений, AI-интерпретации и уведомлений
 * из `backend/app/schemas.py` (§9 Readme.md).
 */

export type DecisionType = 'hire' | 'maintenance' | 'other';

export type DecisionVerdict = 'effective' | 'ineffective' | 'pending';

export interface DecisionDto {
  id: string | null;
  scenario_id: string;
  type: DecisionType;
  params: Record<string, number | string>;
  owner: string;
  due_date: string | null;
  expected_effect_byn: number;
  notes: string | null;
  baseline_snapshot: Record<string, number> | null;
  actual_effect_byn: number;
  verdict: DecisionVerdict;
  created_at: string | null;
  jira_key: string | null;
}

export interface SimulationDto {
  days: number;
  branch: 'main' | 'neg';
  effect_byn: number;
  verdict: 'effective' | 'ineffective';
  recommendation: string | null;
  compensating_cause: string | null;
  loss_day: number;
  defect_rate: number;
  downtime_h: number;
  final_snapshot: Record<string, { value: number; status: string }>;
}

export interface AiContextDto {
  scene: string;
  node_id: string;
  chain: string[];
  delta: Record<string, number>;
  cost_per_day: number;
}

export interface AiDto extends AiContextDto {
  interpretation: string;
  source: 'cache' | 'deepseek' | 'fallback';
  cache_hit: boolean;
}

export interface AiHealthDto {
  enabled: boolean;
  model: string;
  cache_size: number;
  provider: string;
}

export interface NotificationDto {
  id: string;
  channel: 'telegram' | 'email' | 'inapp';
  recipient: string;
  subject: string;
  body: string;
  status: 'sent' | 'failed' | 'skipped_no_token';
  created_at: string;
  related_decision_id: string | null;
}