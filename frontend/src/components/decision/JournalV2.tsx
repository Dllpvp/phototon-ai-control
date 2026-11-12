import { useState } from "react";
import { motion } from "framer-motion";
import { useMotionReduced } from "../../lib/motion";

/**
 * Статусы решений
 */
export type DecisionStatus = "draft" | "in_progress" | "done" | "rejected";

/**
 * Тип записи журнала решений
 */
export type DecisionRecord = {
  id: string;
  action: string;
  responsible: string;
  deadline: string;
  status: DecisionStatus;
  verdict?: string;
};

/**
 * Пропсы для JournalV2
 */
type JournalV2Props = {
  decisions: DecisionRecord[];
  onAdvance?: (id: string, newStatus: DecisionStatus) => void;
};

/**
 * Маппинг статусов на лейблы и классы бейджей
 */
const STATUS_CONFIG: Record<DecisionStatus, { label: string; class: string }> = {
  draft: { label: "Черновик", class: "badge-accent" },
  in_progress: { label: "В работе", class: "badge-warn" },
  done: { label: "Выполнено", class: "badge-ok" },
  rejected: { label: "Отклонено", class: "badge-alert" },
};

/**
 * Логика перевода статусов
 */
const getNextStatus = (current: DecisionStatus): DecisionStatus => {
  switch (current) {
    case "draft": return "in_progress";
    case "in_progress": return "done";
    case "done": return "draft"; // цикл для демо
    case "rejected": return "draft";
    default: return "draft";
  }
};

/**
 * JournalV2 — «Журнал решений».
 * Клик статуса → перевод на следующий этап.
 */
export function JournalV2({ decisions, onAdvance }: JournalV2Props) {
  const [records, setRecords] = useState<DecisionRecord[]>(decisions);
  const reduced = useMotionReduced();

  const handleStatusClick = async (id: string, currentStatus: DecisionStatus) => {
    const nextStatus = getNextStatus(currentStatus);

    // Оптимистичное обновление UI
    setRecords((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: nextStatus } : r))
    );

    // Имитация запроса к API (POST /api/simulate/advance)
    try {
      await fetch("/api/simulate/advance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, status: nextStatus }),
      });
      onAdvance?.(id, nextStatus);
    } catch (error) {
      // Откат при ошибке сети
      setRecords((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: currentStatus } : r))
      );
    }
  };

  if (records.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <p style={{ color: "var(--muted)" }}>Журнал решений пуст</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: "1.5rem" }}>
      {/* Заголовок */}
      <h3
        style={{
          fontSize: "1.25rem",
          fontWeight: 600,
          color: "var(--text)",
          marginBottom: "1rem",
        }}
      >
        Журнал решений
      </h3>

      {/* Таблица */}
      <table className="journal-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Действие</th>
            <th>Ответственный</th>
            <th>Срок</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => {
            const config = STATUS_CONFIG[record.status];

            return (
              <motion.tr
                key={record.id}
                whileHover={!reduced ? { backgroundColor: "var(--panel-2)" } : undefined}
                transition={{ duration: 0.15 }}
              >
                <td
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.8rem",
                    color: "var(--muted)",
                  }}
                >
                  {record.id}
                </td>
                <td style={{ fontWeight: 500 }}>{record.action}</td>
                <td>{record.responsible}</td>
                <td
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.875rem",
                  }}
                >
                  {record.deadline}
                </td>
                <td>
                  <span
                    className={`badge ${config.class}`}
                    onClick={() => handleStatusClick(record.id, record.status)}
                    style={{ cursor: "pointer", userSelect: "none" }}
                    title="Нажмите для перевода статуса"
                  >
                    {config.label}
                  </span>
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}