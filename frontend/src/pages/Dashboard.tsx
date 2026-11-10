import { Link } from "react-router";

import { useDashboard, useForecast } from "../api/queries";
import { AlertsColumn } from "../components/dashboard/AlertsColumn";
import { ChainPanel } from "../components/chain/ChainPanel";
import { ForecastCard } from "../components/dashboard/ForecastCard";
import { KpiGrid } from "../components/dashboard/KpiGrid";
import { LossCounter } from "../components/dashboard/LossCounter";
import { UnitEconTable } from "../components/dashboard/UnitEconTable";
import { JournalTable } from "../components/decision/JournalTable";
import { DecisionForm } from "../components/decision/DecisionForm";
import { DemoBadge } from "../components/layout/DemoBadge";
import { Section } from "../components/layout/Section";
import { WhatIfSlider } from "../components/whatif/WhatIfSlider";
import { useUIStore } from "../store/ui";

function SkeletonLine({ width }: { width: string }) {
  return <div className="h-3" style={{ width, background: "var(--panel-2)", borderRadius: "var(--radius)" }} />;
}

function HeroRow() {
  const scenario = useUIStore((state) => state.scenario);
  const query = useDashboard(scenario);
  const lossKpi = query.data?.kpis.find((kpi) => kpi.node_id === "fin_loss_day");
  return <Section title="Сводка недели" subtitle={<span className="mono">{query.data?.headline ?? "—"}</span>} className="col-span-full"><div className="flex flex-wrap items-end justify-between gap-6">{query.data && lossKpi ? <LossCounter lossDay={lossKpi.value} startedAt={query.data.loss_counter_started_at} /> : <div className="flex flex-col gap-1" style={{ minWidth: 0 }}><SkeletonLine width="9rem" /><SkeletonLine width="14rem" /></div>}<DemoBadge /></div></Section>;
}

function ChainPanelSection() {
  const selectedNodeId = useUIStore((state) => state.selectedNodeId);
  const asOf = useUIStore((state) => state.as_of);
  if (!selectedNodeId) return null;
  return <Section title="Цепочка причины" subtitle={asOf ? <span className="mono">{asOf}</span> : "—"} className="col-span-full"><ChainPanel selectedNodeId={selectedNodeId} /></Section>;
}

function WhatIfSection() {
  return <Section title="What-If" subtitle="ползунок ↓" className="col-span-full"><WhatIfSlider /></Section>;
}

function ForecastSection() {
  const scenario = useUIStore((state) => state.scenario);
  return <Section title="Прогноз" subtitle="4 недели"><ForecastCard query={useForecast(scenario)} /></Section>;
}

export default function Dashboard() {
  const scenario = useUIStore((state) => state.scenario);
  const selectNode = useUIStore((state) => state.selectNode);
  const setOpenDecisionForm = useUIStore((state) => state.setOpenDecisionForm);
  const query = useDashboard(scenario);
  return <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
    <HeroRow />
    <Section title="KPI" subtitle={`${query.data?.kpis.length ?? 0} метрик`} className="col-span-full lg:col-span-2"><KpiGrid query={query} /></Section>
    <Section title="Алерты" subtitle={`${query.data?.alerts.length ?? 0}`}><AlertsColumn query={query} onSelect={selectNode} /></Section>
    <ChainPanelSection />
    <WhatIfSection />
    <ForecastSection />
    <Section title="Юнит-экономика" subtitle="маржа по SKU, %"><UnitEconTable /></Section>
    <Section title="Журнал" subtitle="последние решения"><JournalTable /><div className="mt-3 flex justify-between"><button type="button" className="tag" style={{ color: "var(--accent)" }} onClick={() => setOpenDecisionForm(true)}>Оформить решение</button><Link className="mono text-xs" style={{ color: "var(--accent)" }} to="/journal">весь журнал →</Link></div></Section>
    <DecisionForm />
  </div>;
}
