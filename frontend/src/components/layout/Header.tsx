import { useQueryClient } from "@tanstack/react-query";
import { Shield } from "lucide-react";
import { useState } from "react";

import { useDecisions, useSimulate } from "../../api/queries";
import { useDemoStore } from "../../store/demo";
import { useUIStore } from "../../store/ui";
import { SecurityAuditModal } from "../security/SecurityAuditModal";
import { RoleSwitcher } from "./RoleSwitcher";
import { ThemeSwitcher } from "./ThemeSwitcher";

export function Header() {
  const resetDemo = useDemoStore((state) => state.resetDemo);
  const openSimulateModal = useDemoStore((state) => state.openSimulateModal);
  const setSimulateSuccess = useDemoStore((state) => state.setSimulateSuccess);
  const setSimulateError = useDemoStore((state) => state.setSimulateError);
  const currentScenario = useUIStore((state) => state.scenario);
  const queryClient = useQueryClient();
  const { data: decisions } = useDecisions(currentScenario);
  const simulate = useSimulate();
  const [auditOpen, setAuditOpen] = useState(false);

  const handlePlus14Days = () => {
    const hireDecisions = (decisions ?? []).filter((decision) => decision.type === "hire");
    const decision = hireDecisions[hireDecisions.length - 1];
    if (!decision?.id) {
      useDemoStore.getState().setSimulateEmpty("Сначала оформите решение типа «Найм» в журнале.");
      return;
    }

    openSimulateModal(decision);
    simulate.mutate(
      { id: decision.id, params: { days: 14, branch: "main" } },
      {
        onSuccess: (result) => {
          setSimulateSuccess("main", result);
          queryClient.invalidateQueries();
        },
        onError: (error) => setSimulateError(error.message),
      },
    );
  };

  const handlePdfExport = () => {
    window.open(`/api/report/executive.pdf?scenario=${encodeURIComponent(currentScenario)}`, "_blank");
  };

  const handleReset = () => {
    resetDemo();
    useUIStore.getState().reset();
    queryClient.invalidateQueries();
  };

  return (
    <header className="flex items-center justify-between px-4 py-3" style={{ borderBottom: "1px solid var(--hair)" }}>
      <div className="flex items-baseline gap-3">
        <span className="display text-lg font-bold tracking-tight">Фотопринт·Контроль</span>
        <span className="mono text-xs" style={{ color: "var(--muted)" }}>неделя 45 · 02.11.2026</span>
      </div>
      <div className="flex items-center gap-2">
        <RoleSwitcher />
        <button
          type="button"
          className="tag flex items-center gap-1"
          style={{ color: "var(--accent)", cursor: "pointer" }}
          onClick={() => setAuditOpen(true)}
          title="Журнал аудита LLM (только директор)"
        >
          <Shield size={14} />
          <span className="mono text-xs">Аудит</span>
        </button>
        <ThemeSwitcher />
        <button type="button" className="tag" style={{ color: "var(--accent)", cursor: "pointer" }} onClick={handlePlus14Days}>⏩ +14 дней</button>
        <button type="button" className="tag" style={{ color: "var(--accent)", cursor: "pointer" }} onClick={handlePdfExport}>PDF</button>
        <button type="button" className="tag" style={{ color: "var(--accent)", cursor: "pointer" }} onClick={handleReset}>Сброс демо</button>
      </div>
      <SecurityAuditModal open={auditOpen} onClose={() => setAuditOpen(false)} />
    </header>
  );
}
