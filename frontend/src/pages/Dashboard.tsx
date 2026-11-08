/** Скелет Dashboard (§10.2). Данные появятся на этапе 5 (T5.x). */
import { Link } from "react-router";

import { DemoBadge } from "../components/layout/DemoBadge";
import { Section } from "../components/layout/Section";

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
  return (
    <Section
      title="Сводка недели"
      subtitle={<span className="mono">—</span>}
      className="col-span-full"
    >
      <div className="flex flex-wrap items-end gap-6">
        <div>
          <div className="mono text-xs" style={{ color: "var(--muted)" }}>
            Потери недели
          </div>
          <div className="mono text-3xl">—</div>
        </div>
        <div>
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

function KpiGrid() {
  return (
    <Section title="KPI" subtitle="4 метрики" className="col-span-full lg:col-span-2">
      <div className="grid grid-cols-2 gap-3">
        {["Выручка", "Маржа", "Потери", "Заказы"].map((label) => (
          <div key={label} className="p-3" style={{ border: "1px solid var(--hair)" }}>
            <div className="mono text-xs" style={{ color: "var(--muted)" }}>
              {label}
            </div>
            <div className="mono text-xl">—</div>
            <SkeletonLine width="60%" />
          </div>
        ))}
      </div>
    </Section>
  );
}

function AlertsColumn() {
  return (
    <Section title="Алерты" subtitle="—">
      <ul className="flex flex-col gap-2">
        {[0, 1, 2].map((i) => (
          <li key={i} className="p-2" style={{ border: "1px solid var(--hair)" }}>
            <PlaceholderText>нет данных</PlaceholderText>
            <SkeletonLine width="80%" />
          </li>
        ))}
      </ul>
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
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <HeroRow />
      <KpiGrid />
      <AlertsColumn />
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