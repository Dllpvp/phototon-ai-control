/** Шаг демо-сценария, роль/отдел демо-RBAC и временные результаты симуляции. */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { DecisionDTO, DemoDept, DemoRole, SimulationDTO } from "../api/types";

export type PrefilledDecision =
  | { type: "hire"; params: { operators: number; shift: number } }
  | { type: "maintenance"; params: Record<string, unknown> }
  | { type: "other"; params: Record<string, unknown> };
export type SimulateBranch = "main" | "neg";
export type SimulateModalState = "idle" | "loading" | "success" | "error" | "empty";

interface DemoState {
  /** Демо-роль (§22.3): единственный источник правды для UI и заголовков X-Demo-Role. */
  role: DemoRole;
  /** Отдел для роли department_head (X-Demo-Dept); иначе null. */
  dept: DemoDept | null;
  setRole: (role: DemoRole) => void;
  setDept: (dept: DemoDept | null) => void;
  step: number;
  prefilledDecision: PrefilledDecision | null;
  resetNonce: number;
  simulateModalOpen: boolean;
  simulateModalState: SimulateModalState;
  simulateDecision: DecisionDTO | null;
  simulateMain: SimulationDTO | null;
  simulateNeg: SimulationDTO | null;
  activeSimulateBranch: SimulateBranch;
  simulateErrorMessage: string | null;
  next: () => void;
  setStep: (step: number) => void;
  setPrefilledDecision: (decision: PrefilledDecision | null) => void;
  resetDemo: () => void;
  openSimulateModal: (decision: DecisionDTO) => void;
  closeSimulateModal: () => void;
  setSimulateLoading: (branch: SimulateBranch) => void;
  setSimulateSuccess: (branch: SimulateBranch, simulation: SimulationDTO) => void;
  setSimulateError: (message: string) => void;
  setSimulateEmpty: (message?: string) => void;
}

export const useDemoStore = create<DemoState>()(
  persist(
    (set) => ({
      role: "director",
      dept: null,
      setRole: (role) =>
        set((state) => ({ role, dept: role === "department_head" ? state.dept : null })),
      setDept: (dept) => set({ dept }),
      step: 0,
      prefilledDecision: null,
      resetNonce: 0,
      simulateModalOpen: false,
      simulateModalState: "idle",
      simulateDecision: null,
      simulateMain: null,
      simulateNeg: null,
      activeSimulateBranch: "main",
      simulateErrorMessage: null,
      next: () => set((state) => ({ step: state.step + 1 })),
      setStep: (step) => set({ step }),
      setPrefilledDecision: (prefilledDecision) => set({ prefilledDecision }),
      resetDemo: () => set((state) => ({
        role: "director",
        dept: null,
        step: 0,
        prefilledDecision: null,
        resetNonce: state.resetNonce + 1,
        simulateModalOpen: false,
        simulateModalState: "idle",
        simulateDecision: null,
        simulateMain: null,
        simulateNeg: null,
        activeSimulateBranch: "main",
        simulateErrorMessage: null,
      })),
      openSimulateModal: (decision) => set({
        simulateModalOpen: true,
        simulateDecision: decision,
        simulateModalState: "loading",
        simulateMain: null,
        simulateNeg: null,
        activeSimulateBranch: "main",
        simulateErrorMessage: null,
      }),
      closeSimulateModal: () => set({ simulateModalOpen: false }),
      setSimulateLoading: (branch) => set({
        activeSimulateBranch: branch,
        simulateModalState: "loading",
        simulateErrorMessage: null,
      }),
      setSimulateSuccess: (branch, simulation) => set((state) => ({
        activeSimulateBranch: branch,
        simulateModalState: "success",
        simulateMain: branch === "main" ? simulation : state.simulateMain,
        simulateNeg: branch === "neg" ? simulation : state.simulateNeg,
        simulateErrorMessage: null,
      })),
      setSimulateError: (simulateErrorMessage) =>
        set({ simulateModalState: "error", simulateErrorMessage }),
      setSimulateEmpty: (simulateErrorMessage) =>
        set({ simulateModalState: "empty", simulateErrorMessage: simulateErrorMessage ?? null }),
    }),
    {
      name: "fotoprint-demo",
      // Роль/отдел персистятся: после refresh демо остаётся в той же роли.
      partialize: (state) => ({
        role: state.role,
        dept: state.dept,
        step: state.step,
        prefilledDecision: state.prefilledDecision,
        resetNonce: state.resetNonce,
      }),
    },
  ),
);
