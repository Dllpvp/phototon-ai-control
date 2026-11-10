/** Шаг демо-сценария (T8.1). Без persist — сбрасывается при перезагрузке. */
import { create } from "zustand";

/** Черновик решения, переносимый из What-If в форму (§10.4, T5.4). */
export interface PrefilledDecision {
  type: "hire";
  params: { operators: number; shift: number };
}

interface DemoState {
  step: number;
  prefilledDecision: PrefilledDecision | null;
  next: () => void;
  reset: () => void;
  setStep: (n: number) => void;
  setPrefilledDecision: (d: PrefilledDecision | null) => void;
}

export const useDemoStore = create<DemoState>((set) => ({
  step: 0,
  prefilledDecision: null,
  next: () => set((s) => ({ step: s.step + 1 })),
  reset: () => set({ step: 0, prefilledDecision: null }),
  setStep: (step) => set({ step }),
  setPrefilledDecision: (prefilledDecision) => set({ prefilledDecision }),
}));