/** Dashboard — живые данные поверх скелета (§10.2–10.9, T5.x).
 *  Секции подключаются по мере готовности подзадач.
 */
import { Link } from "react-router";

import { useDashboard } from "../api/queries";
import { AlertsColumn } from "../components/dashboard/AlertsColumn";
import { KpiGrid } from "../components/dashboard/KpiGrid";
import { DemoBadge } from "../components/layout/DemoBadge";
import { Section } from "../components/layout/Section";
import { useUIStore } from "../store/ui";

function SkeletonLine({ width }: { width: string }) {
  return (
    <div
      className="h-3"
      style={{ width, background: "var(--panel-2)", borderRadius: "var(--radius)" }}
    />
  );
}

function PlaceholderText({ children }: { children: string }) {
  return (
    <p className="mono text-sm" style={{ color: "var(--muted)" }}>
      {children}
    </p>
  );
}

function HeroRow() {
  const scenario = useUIStore((s) => s.scenario);
  const query = useDashboard(scenario);
  return (
    <Section
      title="Сводка недели"
      subtitle={<span className="mono">{query.data?.headline ?? "—"}</span>}
      className="col-span-full"
    >
      <div className="flex flex-wrap items-end gap-6">
        <div style={{ minWidth: 0 }}>
          <div className="mono text-xs" style={{ color: "var(--muted)" }}>
            Потери недели
          </div>
          <div className="mono text-3xl">—</div>
        </div>
        <div style={{ minWidth: 0 }}>
          <div className="mono text-xs" style={{ color: "var(--muted)" }}>
            Маржа
          </div>
          <div className="mono text-3xl">—</div>
        </div>
        <DemoBadge />
      </div>
    </Section>
  );
}

function WhatIfSection() {
  return (
    <Section title="What-If" subtitle="ползунок ↓" className="col-span-full">
      <div
        className="h-2 w-full"
        style={{ background: "var(--panel-2)", borderRadius: "var(--radius)" }}
      />
      <div className="mt-3">
        <PlaceholderText>эффект решения: —</PlaceholderText>
      </div>
    </Section>
  );
}

export default function Dashboard() {
  const scenario = useUIStore((s) => s.scenario);
  const selectNode = useUIStore((s) => s.selectNode);
  const query = useDashboard(scenario);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <HeroRow />
      <Section
        title="KPI"
        subtitle={`${query.data?.kpis.length ?? 0} метрик`}
        className="col-span-full lg:col-span-2"
      >
        <KpiGrid query={query} />
      </Section>
      <Section title="Алерты" subtitle={`${query.data?.alerts.length ?? 0}`}>
        <AlertsColumn query={query} onSelect={selectNode} />
      </Section>
      <WhatIfSection />
      <Section title="Прогноз" subtitle="4 недели">
        <SkeletonLine width="100%" />
      </Section>
      <Section title="Юнит-экономика" subtitle="—">
        <SkeletonLine width="100%" />
      </Section>
      <Section title="Журнал" subtitle="последние решения">
        <PlaceholderText>записей нет</PlaceholderText>
        <Link className="mono text-xs" style={{ color: "var(--accent)" }} to="/journal">
          весь журнал →
        </Link>
      </Section>
    </div>
  );
}
