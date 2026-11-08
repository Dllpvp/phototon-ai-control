import { useParams } from "react-router";

import { Section } from "../components/layout/Section";

export default function DecisionPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <Section title="Решение" subtitle={`#${id ?? "—"}`}>
      <p className="mono text-sm" style={{ color: "var(--muted)" }}>
        Диплинк /decision/:id (T5).
      </p>
    </Section>
  );
}