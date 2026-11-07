import { useThemeStore, type ThemeId } from "../../store/theme";
import { cn } from "../../lib/cn";

const THEMES: { id: ThemeId; label: string; hint: string }[] = [
  { id: "mission",  label: "ПУЛЬТ",    hint: "цех / телеметрия" },
  { id: "swiss",    label: "СВОДКА",   hint: "директор / отчёт" },
  { id: "investor", label: "ИНВЕСТОР", hint: "совет директоров" },
  { id: "zen",      label: "ДЗЕН",     hint: "скандинавский вайб" },
];

export function ThemeSwitcher() {
  const { theme, mode, setTheme, toggleMode } = useThemeStore();
  return (
    <div className="flex items-center gap-3 mono text-[11px]">
      <div className="flex border border-[var(--hair)] rounded-[var(--radius)] overflow-hidden">
        {THEMES.map((t) => (
          <button
            key={t.id}
            onClick={() => setTheme(t.id)}
            title={t.hint}
            className={cn(
              "px-3 py-1.5 uppercase tracking-wide transition-colors",
              theme === t.id
                ? "bg-[var(--text)] text-[var(--bg)]"
                : "text-[var(--muted)] hover:bg-[var(--panel-2)]"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>
      <button
        onClick={toggleMode}
        aria-label="переключить режим"
        className="px-2 py-1.5 border border-[var(--hair)] rounded-[var(--radius)] text-[var(--muted)] hover:text-[var(--text)]"
      >
        {mode === "dark" ? "☾" : "☀"}
      </button>
    </div>
  );
}