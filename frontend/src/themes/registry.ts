/** Реестр тем (PLAN-V2 §21.5, R18). Форма записи — как у тем в ThemeSwitcher + enabled/default. */
import type { Mode, ThemeId } from "../store/theme";

export interface ThemeEntry {
  id: ThemeId;
  label: string;
  hint: string;
  enabled: boolean;
  default?: boolean;
}

export const themes: ThemeEntry[] = [
  { id: "fotoprint", label: "Фотопринт", hint: "бренд-тема", enabled: true, default: true },
  { id: "mission",   label: "ПУЛЬТ",     hint: "цех / телеметрия",   enabled: true },
  { id: "swiss",     label: "СВОДКА",    hint: "директор / отчёт",   enabled: true },
  { id: "investor",  label: "ИНВЕСТОР",  hint: "совет директоров",   enabled: true },
  { id: "zen",       label: "ДЗЕН",      hint: "скандинавский вайб", enabled: true },
];

export const defaultThemeId: ThemeId = "fotoprint";
export const defaultMode: Mode = "light";

export function isThemeEnabled(id: ThemeId): boolean {
  return themes.some((t) => t.id === id && t.enabled);
}
