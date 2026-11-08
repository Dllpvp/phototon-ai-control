import { useToastStore } from "../components/layout/Toast";
import { Section } from "../components/layout/Section";

export default function ReportPage() {
  const push = useToastStore((s) => s.push);
  return (
    <Section title="Отчёт" subtitle="PDF / CSV">
      <p className="mono text-sm" style={{ color: "var(--muted)" }}>
        Генерация отчётов появится в T6.
      </p>
      <button
        type="button"
        className="mono mt-3 text-sm"
        style={{
          padding: "0.5rem 1rem",
          border: "1px solid var(--hair)",
          color: "var(--text)",
          cursor: "pointer",
          background: "var(--panel-2)",
        }}
        onClick={() => push({ kind: "info", text: "PDF-экспорт в разработке" })}
      >
        Скачать PDF
      </button>
    </Section>
  );
}