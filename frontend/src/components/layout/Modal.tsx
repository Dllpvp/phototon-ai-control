/** Модальное окно на портале. 4 состояния: loading / empty / error / success. */
import { useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { cn } from "../../lib/cn";

export type ModalState = "loading" | "empty" | "error" | "success";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  state?: ModalState;
  children?: ReactNode;
  /** Текст ошибки/пустоты для соответствующего состояния. */
  message?: string;
}

const STATE_ACCENT: Record<ModalState, string> = {
  loading: "var(--muted)",
  empty: "var(--muted)",
  error: "var(--alert)",
  success: "var(--ok)",
};

const STATE_LABEL: Record<ModalState, string> = {
  loading: "Загрузка",
  empty: "Пусто",
  error: "Ошибка",
  success: "Готово",
};

export function Modal({ open, onClose, title, state = "success", children, message }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "color-mix(in srgb, var(--bg) 70%, transparent)" }}
      onClick={onClose}
    >
      <div
        className="card w-full max-w-lg"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <header
          className="flex items-center justify-between px-4 py-3"
          style={{ borderBottom: "1px solid var(--hair)" }}
        >
          <span className="display font-semibold" style={{ color: "var(--text)" }}>
            {title ?? "Диалог"}
          </span>
          <span className="tag" style={{ color: STATE_ACCENT[state] }}>
            {STATE_LABEL[state]}
          </span>
        </header>
        <div className="p-4" style={{ color: "var(--text)" }}>
          {state === "loading" && (
            <div className="flex items-center gap-2">
              <span className="live-dot" />
              <span className="mono text-sm" style={{ color: "var(--muted)" }}>
                {message ?? "Загрузка данных…"}
              </span>
            </div>
          )}
          {state === "empty" && (
            <p className="mono text-sm" style={{ color: "var(--muted)" }}>
              {message ?? "Нет данных для отображения"}
            </p>
          )}
          {state === "error" && (
            <p className="mono text-sm" style={{ color: "var(--alert)" }}>
              {message ?? "Не удалось загрузить данные"}
            </p>
          )}
          {state === "success" && (
            <div className={cn("text-sm")}>{children ?? message ?? "Операция выполнена"}</div>
          )}
        </div>
        <footer
          className="flex justify-end px-4 py-3"
          style={{ borderTop: "1px solid var(--hair)" }}
        >
          <button
            type="button"
            className="tag"
            style={{ color: "var(--accent)", cursor: "pointer" }}
            onClick={onClose}
          >
            Закрыть
          </button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}