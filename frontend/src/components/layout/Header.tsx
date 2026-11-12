import { useState } from "react";
import { SystemNav } from "./SystemNav";

/**
 * Пропсы для Header
 */
type HeaderProps = {
  onOpenDecisionForm: () => void;
  onOpenJournal: () => void;
};

/**
 * Header — верхняя панель управления.
 * Лого + ◐ режим, pill SystemNav, кнопки действий.
 */
export function Header({ onOpenDecisionForm, onOpenJournal }: HeaderProps) {
  const [mode, setMode] = useState<"light" | "dark">("dark");

  const toggleMode = () => {
    const newMode = mode === "dark" ? "light" : "dark";
    setMode(newMode);
    document.documentElement.setAttribute("data-mode", newMode);
  };

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "1rem 2rem",
        background: "var(--panel)",
        borderBottom: "1px solid var(--hair)",
        gap: "1.5rem",
      }}
    >
      {/* Левая часть: Лого + Переключатель режима */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            fontWeight: 700,
            fontSize: "1.25rem",
            color: "var(--text)",
          }}
        >
          {/* Лого (SVG иконка) */}
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <line x1="3" y1="9" x2="21" y2="9" />
            <line x1="9" y1="21" x2="9" y2="9" />
          </svg>
          <span>PhotoTon AI</span>
        </div>

        {/* Переключатель режима (◐) */}
        <button
          onClick={toggleMode}
          aria-label="Переключить режим"
          style={{
            background: "var(--panel-2)",
            border: "1px solid var(--hair)",
            borderRadius: "var(--radius)",
            width: "32px",
            height: "32px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            color: "var(--text)",
            fontSize: "1rem",
          }}
        >
          ◐
        </button>
      </div>

      {/* Центр: Pill-навигация */}
      <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
        <SystemNav />
      </div>

      {/* Правая часть: Кнопки действий */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <button
          onClick={onOpenDecisionForm}
          style={{
            background: "var(--accent)",
            color: "var(--text)",
            border: "none",
            borderRadius: "var(--radius)",
            padding: "0.5rem 1rem",
            fontWeight: 600,
            fontSize: "0.875rem",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLButtonElement).style.opacity = "0.9";
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLButtonElement).style.opacity = "1";
          }}
        >
          Оформить решение
        </button>

        <button
          onClick={onOpenJournal}
          style={{
            background: "var(--panel-2)",
            color: "var(--text)",
            border: "1px solid var(--hair)",
            borderRadius: "var(--radius)",
            padding: "0.5rem 1rem",
            fontWeight: 600,
            fontSize: "0.875rem",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLButtonElement).style.borderColor = "var(--hair-strong)";
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLButtonElement).style.borderColor = "var(--hair)";
          }}
        >
          Журнал решений
        </button>
      </div>
    </header>
  );
}