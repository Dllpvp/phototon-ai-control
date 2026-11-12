/** Шаг демо-сценария и временные результаты симуляции. */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { DecisionDTO, SimulationDTO } from "../api/types";

export type PrefilledDecision =
  | { type: "hire"; params: { operators: number; shift: number } }
  | { type: "maintenance"; params: Record<string, unknown> }
  | { type: "other"; params: Record<string, unknown> };

export type SimulateBranch = "main" | "neg";
export type SimulateModalState = "idle" | "loading" | "success" | "error" | "empty";

export type DemoRole =
  | "director"
  | "department_head"
  | "production_head"
  | "hr_head"
  | "finance_head"
  | "support_head"
  | "specialist";

interface DemoState {
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
  
  // Новые поля для RBAC и навигации
  currentTab: string;
  role: DemoRole;
  dept: string | null;
  
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
  
  // Новые сеттеры
  setCurrentTab: (id: string) => void;
  setRole: (role: DemoRole) => void;
  setDept: (dept: string | null) => void;
}

export const useDemoStore = create<DemoState>()(
  persist(
    (set) => ({
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
      
      // Дефолтные значения для RBAC
      currentTab: "overview",
      role: "director",
      dept: null,

      next: () => set((state) => ({ step: state.step + 1 })),
      setStep: (step) => set({ step }),
      setPrefilledDecision: (prefilledDecision) => set({ prefilledDecision }),
      
      resetDemo: () => set((state) => ({
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
        currentTab: "overview",
        role: "director",
        dept: null,
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
      setSimulateLoading: (branch) => set({ activeSimulateBranch: branch, simulateModalState: "loading", simulateErrorMessage: null }),
      setSimulateSuccess: (branch, simulation) => set((state) => ({
        activeSimulateBranch: branch,
        simulateModalState: "success",
        simulateMain: branch === "main" ? simulation : state.simulateMain,
        simulateNeg: branch === "neg" ? simulation : state.simulateNeg,
        simulateErrorMessage: null,
      })),
      setSimulateError: (simulateErrorMessage) => set({ simulateModalState: "error", simulateErrorMessage }),
      setSimulateEmpty: (simulateErrorMessage) => set({ simulateModalState: "empty", simulateErrorMessage: simulateErrorMessage ?? null }),
      
      // Новые сеттеры
      setCurrentTab: (currentTab) => set({ currentTab }),
      setRole: (role) => set({ role }),
      setDept: (dept) => set({ dept }),
    }),
    { 
      name: "fotoprint-demo",
      partialize: (state) => ({
        currentTab: state.currentTab,
        role: state.role,
        dept: state.dept,
      })
    }
  )
);