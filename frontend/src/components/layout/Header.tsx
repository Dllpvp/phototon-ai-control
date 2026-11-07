import { ThemeSwitcher } from "./ThemeSwitcher";

export function Header() {
  return (
    <header
      className="flex items-center justify-between px-4 py-3"
      style={{ borderBottom: "1px solid var(--hair)" }}
    >
      <div className="flex items-baseline gap-3">
        <span className="display text-lg font-bold tracking-tight">
          Фотопринт·Контроль
        </span>
        <span className="mono text-xs" style={{ color: "var(--muted)" }}>
          неделя 45 · 02.11.2026
        </span>
      </div>
      <ThemeSwitcher />
    </header>
  );
}
