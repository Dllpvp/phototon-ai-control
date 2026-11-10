/** UI-состояние: сценарий, дата, выбранный узел, кросс-фильтр (§10.2). */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ScenarioId } from "../api/types";

export interface SliceFilter {
  week: number | null;
  line: string | null;
  shift: number | null;
}

interface UIState {
  scenario: ScenarioId;
  as_of: string | null;
  selectedNodeId: string | null;
  sliceFilter: SliceFilter;
  openDecisionForm: boolean;
  setScenario: (s: ScenarioId) => void;
  setAsOf: (d: string | null) => void;
  selectNode: (id: string | null) => void;
  setSliceFilter: (f: Partial<SliceFilter>) => void;
  setOpenDecisionForm: (v: boolean) => void;
  reset: () => void;
}

const INITIAL = {
  scenario: "main" as ScenarioId,
  as_of: null,
  selectedNodeId: null,
  sliceFilter: { week: null, line: null, shift: null } as SliceFilter,
  openDecisionForm: false,
};

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      ...INITIAL,
      setScenario: (scenario) => set({ scenario, selectedNodeId: null }),
      setAsOf: (as_of) => set({ as_of }),
      selectNode: (selectedNodeId) => set({ selectedNodeId }),
      setSliceFilter: (f) => set((s) => ({ sliceFilter: { ...s.sliceFilter, ...f } })),
      setOpenDecisionForm: (v) => set({ openDecisionForm: v }),
      reset: () => set({ ...INITIAL }),
    }),
    {
      name: "fotoprint-ui",
      // Персистим только выбранный сценарий (AGENTS.md: scenario персистится).
      partialize: (s) => ({ scenario: s.scenario }),
    },
  ),
);