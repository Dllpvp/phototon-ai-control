import { useState } from "react";
import { motion } from "framer-motion";
import { useMotionReduced } from "../../lib/motion";
import type { DecisionRecord, DecisionRecordStatus } from "../../lib/adapters";

type JournalV2Props = {
  decisions: DecisionRecord[];
  onAdvance?: (id: string, newStatus: DecisionRecordStatus) => void;
};

const STATUS_CONFIG: Record<DecisionRecordStatus, { label: string; class: string }> = {
  pending: { label: "Ожидает", class: "badge-accent" },
  effective: { label: "Эффективно", class: "badge-ok" },
  ineffective: { label: "Неэффективно", class: "badge-alert" },
};

const getNextStatus = (current: DecisionRecordStatus): DecisionRecordStatus => {
  switch (current) {
    case "pending": return "effective";
    case "effective": return "ineffective";
    case "ineffective": return "pending";
    default: return "pending";
  }
};

export function JournalV2({ decisions, onAdvance }: JournalV2Props) {
  const [records, setRecords] = useState<DecisionRecord[]>(decisions);
  const reduced = useMotionReduced();

  const handleStatusClick = async (id: string, currentStatus: DecisionRecordStatus) => {
    const nextStatus = getNextStatus(currentStatus);

    setRecords((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: nextStatus } : r))
    );

    try {
      await fetch("/api/simulate/advance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, status: nextStatus }),
      });
      onAdvance?.(id, nextStatus);
    } catch {
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
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>
        Журнал решений
      </h3>

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
                <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--muted)" }}>
                  {record.jiraKey ?? record.id.slice(0, 8)}
                </td>
                <td style={{ fontWeight: 500 }}>{record.action}</td>
                <td>{record.responsible}</td>
                <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.875rem" }}>
                  {record.deadline ?? "—"}
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