/** Служебная страница /devkit — стенд состояний Modal и Toast (T4.4). */
import { useState } from "react";

import { useToastStore, type ToastKind } from "../components/layout/Toast";
import { Modal, type ModalProps } from "../components/layout/Modal";
import { Section } from "../components/layout/Section";

type ModalState = ModalProps["state"];

const MODAL_STATES: Array<{ id: string; state: ModalState }> = [
  { id: "loading", state: "loading" },
  { id: "empty", state: "empty" },
  { id: "error", state: "error" },
  { id: "success", state: "success" },
];

const TOAST_STATES: Array<{ id: string; kind: ToastKind }> = [
  { id: "success", kind: "success" },
  { id: "error", kind: "error" },
  { id: "info", kind: "info" },
];

export default function DevKit() {
  const [open, setOpen] = useState(false);
  const [modalState, setModalState] = useState<ModalState>("success");
  const [modalTitle, setModalTitle] = useState("Диалог");
  const [modalMessage, setModalMessage] = useState("");
  const push = useToastStore((s) => s.push);

  const openModal = (s: (typeof MODAL_STATES)[number]) => {
    setModalState(s.state);
    setModalTitle(s.id.charAt(0).toUpperCase() + s.id.slice(1));
    setModalMessage(
      s.state === "loading"
        ? "Загрузка данных…"
        : s.state === "empty"
          ? "Нет данных для отображения"
          : s.state === "error"
            ? "Не удалось загрузить данные"
            : "Операция выполнена",
    );
    setOpen(true);
  };

  const pushToast = (kind: (typeof TOAST_STATES)[number]["kind"]) => {
    push({
      kind,
      text: kind === "success" ? "Операция выполнена" : kind === "error" ? "Не удалось загрузить" : "Информация",
      detail: "devkit · " + kind,
    });
  };

  return (
    <Section title="DevKit" subtitle="стенд состояний Modal / Toast">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="card p-4">
          <h3 className="display text-sm font-semibold mb-3" style={{ color: "var(--text)" }}>
            Модальное окно (esc / backdrop)
          </h3>
          <div className="flex flex-wrap gap-2">
            {MODAL_STATES.map((s) => (
              <button
                key={s.id}
                type="button"
                className="tag mono text-xs"
                style={{
                  color: "var(--text)",
                  cursor: "pointer",
                  border: "1px solid var(--hair)",
                }}
                onClick={() => openModal(s)}
              >
                {s.id}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="mono mt-3 text-xs"
            style={{ color: "var(--accent)", cursor: "pointer", padding: "0.25rem 0.5rem" }}
            onClick={() => setOpen(false)}
          >
            закрыть модалку
          </button>
        </div>
        <div className="card p-4">
          <h3 className="display text-sm font-semibold mb-3" style={{ color: "var(--text)" }}>
            Тосты (очередь, автоскрытие 4с)
          </h3>
          <div className="flex flex-wrap gap-2">
            {TOAST_STATES.map((t) => (
              <button
                key={t.id}
                type="button"
                className="tag mono text-xs"
                style={{
                  color: "var(--text)",
                  cursor: "pointer",
                  border: "1px solid var(--hair)",
                }}
                onClick={() => pushToast(t.kind)}
              >
                {t.id}
              </button>
            ))}
          </div>
        </div>
        <Modal open={open} onClose={() => setOpen(false)} title={modalTitle} state={modalState}>
          {modalMessage}
        </Modal>
      </div>
    </Section>
  );
}