import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemeId = "mission" | "swiss" | "investor" | "zen" | "fotoprint";
export type Mode = "dark" | "light";

interface ThemeState {
  theme: ThemeId;
  mode: Mode;
  setTheme: (t: ThemeId) => void;
  setMode: (m: Mode) => void;
  toggleMode: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "fotoprint",
      mode: "light",
      setTheme: (theme) => set({ theme }),
      setMode: (mode) => set({ mode }),
      toggleMode: () => set((s) => ({ mode: s.mode === "dark" ? "light" : "dark" })),
    }),
    { name: "fotoprint-theme" }
  )
);

export function applyThemeAttrs(theme: ThemeId, mode: Mode) {
  const el = document.documentElement;
  el.dataset.theme = theme;
  el.dataset.mode = mode;
}
