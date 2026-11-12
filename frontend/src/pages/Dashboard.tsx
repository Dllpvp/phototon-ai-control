import { useState, useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useMotionReduced } from "../lib/motion";

// Layout
import { Header } from "../components/layout/Header";
import { StatSummaryRow } from "../components/layout/StatSummaryRow";

// Data & Chain
import { KpiCardV2, KpiDetailV2 } from "../components/data/KpiCardV2";
import { IndicatorsTable } from "../components/data/IndicatorsTable";
import { WhyDeviation } from "../components/chain/WhyDeviation";
import { CauseCarousel, type Cause } from "../components/chain/CauseCarousel";

// Decisions
import { RequiresDecision } from "../components/decision/RequiresDecision";
import { DecisionFormV2 } from "../components/decision/DecisionFormV2";
import { JournalV2 } from "../components/decision/JournalV2";

// Адаптеры
import {
  toKpiData,
  toTableKpi,
  toDecisionAlert,
  toDecisionRecord,
  toWhyDeviation,
  toChainCause,
} from "../lib/adapters";

// API Hooks
import { useDashboard, useChain, useDecisions } from "../api/queries";

export function Dashboard() {
  const reduced = useMotionReduced();

  const [showForm, setShowForm] = useState(false);
  const [showJournal, setShowJournal] = useState(false);
  const [selectedKpiId, setSelectedKpiId] = useState<string | null>(null);
  const [prefill, setPrefill] = useState<{ causeName?: string; kpiName?: string; description?: string } | undefined>(undefined);

  // Хуки вызываются БЕЗ аргументов — берут scenario/role/dept из стора
  const { data: dashboardData } = useDashboard();
  const { data: chainData } = useChain();
  const { data: decisionsData } = useDecisions();

  // Маппинг через адаптеры
  const kpisData = useMemo(() => {
    const kpis = dashboardData?.kpis ?? [];
    return kpis.map(toKpiData);
  }, [dashboardData]);

  const tableKpis = useMemo(() => {
    const kpis = dashboardData?.kpis ?? [];
    return kpis.map(toTableKpi);
  }, [dashboardData]);

  const alertsData = useMemo(() => {
    const alerts = dashboardData?.alerts ?? [];
    return alerts.map(toDecisionAlert);
  }, [dashboardData]);

  const decisionsRecords = useMemo(() => {
    const decisions = decisionsData ?? [];
    return decisions.map(toDecisionRecord);
  }, [decisionsData]);

  const waterfallData = useMemo(() => toWhyDeviation(chainData), [chainData]);

  const carouselCauses: Cause[] = useMemo(() => {
    if (!chainData || chainData.chain.length === 0) return [];
    return chainData.chain.slice(1).map((n) => ({
      id: n.node_id,
      name: n.name,
      impact: n.delta_from_parent ?? 0,
      domain: n.domain as Cause["domain"],
    }));
  }, [chainData]);

  const handlePrefillFromCause = (cause: Cause) => {
    setPrefill({ causeName: cause.name, description: `Вклад: ${cause.impact}%` });
    setShowForm(true);
  };

  const handlePrefillFromAlert = (alert: ReturnType<typeof toDecisionAlert>) => {
    setPrefill({ kpiName: alert.kpiName, description: alert.description });
    setShowForm(true);
  };

  const selectedKpi = kpisData.find((k) => k.id === selectedKpiId);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", color: "var(--text)" }}>
      <Header
        onOpenDecisionForm={() => { setPrefill(undefined); setShowForm(true); }}
        onOpenJournal={() => setShowJournal(true)}
      />

      <main style={{ maxWidth: "1680px", margin: "0 auto", padding: "24px 32px", display: "flex", flexDirection: "column", gap: "24px" }}>
        <div className="hero-fotoprint">
          <h1 style={{ fontSize: "2.5rem", fontWeight: 700, margin: 0, position: "relative", zIndex: 1 }}>
            PhotoTon AI Control
          </h1>
          <p style={{ fontSize: "1.1rem", margin: "0.5rem 0 0", position: "relative", zIndex: 1 }}>
            Дашборд управления показателями и отклонениями
          </p>
        </div>

        <StatSummaryRow />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1.5rem" }}>
          {kpisData.map((kpi) => (
            <KpiCardV2 key={kpi.id} kpi={kpi} onClick={() => setSelectedKpiId(kpi.id)} />
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem" }}>
          <WhyDeviation data={waterfallData} />
          <CauseCarousel causes={carouselCauses} onPrefillDecision={handlePrefillFromCause} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem" }}>
          <IndicatorsTable kpis={tableKpis} />
          <RequiresDecision alerts={alertsData} onDecision={handlePrefillFromAlert} />
        </div>
      </main>

      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }} onClick={() => setShowForm(false)}>
            <div onClick={(e) => e.stopPropagation()} style={{ width: "100%", maxWidth: "600px" }}>
              <DecisionFormV2 prefill={prefill} onClose={() => setShowForm(false)} onSuccess={() => setShowForm(false)} />
            </div>
          </motion.div>
        )}

        {showJournal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }} onClick={() => setShowJournal(false)}>
            <div onClick={(e) => e.stopPropagation()} style={{ width: "100%", maxWidth: "900px" }}>
              <JournalV2 decisions={decisionsRecords} onAdvance={() => {}} />
            </div>
          </motion.div>
        )}

        {selectedKpi && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }} onClick={() => setSelectedKpiId(null)}>
            <div onClick={(e) => e.stopPropagation()} style={{ width: "100%", maxWidth: "800px" }}>
              <KpiDetailV2 kpi={selectedKpi} onClose={() => setSelectedKpiId(null)} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}