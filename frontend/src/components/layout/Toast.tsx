/** Всплывающие уведомления: очередь, success/error/info, автозакрытие. */
import { useEffect } from "react";
import { createPortal } from "react-dom";
import { create } from "zustand";

export type ToastKind = "success" | "error" | "info";

export interface ToastItem {
  id: number;
  kind: ToastKind;
  text: string;
  /** Дополнительный текст (например, ключ задачи PROD-1234). */
  detail?: string;
}

interface ToastStore {
  items: ToastItem[];
  push: (t: Omit<ToastItem, "id">) => void;
  dismiss: (id: number) => void;
  clear: () => void;
}

let seq = 0;

export const useToastStore = create<ToastStore>((set) => ({
  items: [],
  push: (t) => set((s) => ({ items: [...s.items, { ...t, id: ++seq }] })),
  dismiss: (id) => set((s) => ({ items: s.items.filter((i) => i.id !== id) })),
  clear: () => set({ items: [] }),
}));

const KIND_ACCENT: Record<ToastKind, string> = {
  success: "var(--ok)",
  error: "var(--alert)",
  info: "var(--accent)",
};

const KIND_LABEL: Record<ToastKind, string> = {
  success: "Успех",
  error: "Ошибка",
  info: "Инфо",
};

function ToastCard({ item }: { item: ToastItem }) {
  const dismiss = useToastStore((s) => s.dismiss);

  useEffect(() => {
    const t = setTimeout(() => dismiss(item.id), 4000);
    return () => clearTimeout(t);
  }, [dismiss, item.id]);

  return (
    <div className="card flex items-start gap-3" style={{ padding: "0.75rem 1rem" }}>
      <span className="tag" style={{ color: KIND_ACCENT[item.kind] }}>
        {KIND_LABEL[item.kind]}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm" style={{ color: "var(--text)" }}>
          {item.text}
        </p>
        {item.detail && (
          <p className="mono text-xs" style={{ color: "var(--muted)" }}>
            {item.detail}
          </p>
        )}
      </div>
      <button
        type="button"
        className="mono text-xs"
        style={{ color: "var(--muted)", cursor: "pointer" }}
        onClick={() => dismiss(item.id)}
      >
        ✕
      </button>
    </div>
  );
}

export function ToastQueue() {
  const items = useToastStore((s) => s.items);

  if (items.length === 0) return null;

  return createPortal(
    <div className="fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2">
      {items.map((item) => (
        <ToastCard key={item.id} item={item} />
      ))}
    </div>,
    document.body,
  );
}