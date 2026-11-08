/** Шаг демо-сценария (T8.1). Без persist — сбрасывается при перезагрузке. */
import { create } from "zustand";

interface DemoState {
  step: number;
  next: () => void;
  reset: () => void;
  setStep: (n: number) => void;
}

export const useDemoStore = create<DemoState>((set) => ({
  step: 0,
  next: () => set((s) => ({ step: s.step + 1 })),
  reset: () => set({ step: 0 }),
  setStep: (step) => set({ step }),
}));