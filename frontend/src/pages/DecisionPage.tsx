import { useParams } from "react-router";

import { useDecisions } from "../api/queries";
import type { DecisionDTO } from "../api/types";
import { Section } from "../components/layout/Section";
import { formatByn } from "../lib/format";

function notificationLabel(decision: DecisionDTO): string {
  const notification = decision.notification;
  if (!notification) return "Уведомление отсутствует";
  if (notification.status === "sent") return "Telegram: отправлено";
  if (notification.status === "failed") return "Telegram: ошибка отправки";
  return "Telegram: пропущено (не настроен токен)";
}

export default function DecisionPage() {
  const { id } = useParams<{ id: string }>();
  const { data: decisions, isLoading, isError } = useDecisions();
  const decision = decisions?.find((item) => item.id === id || item.jira_key === id);

  if (isLoading) {
    return <Section title="Решение" subtitle={`#${id ?? "—"}`}><p className="memo">Загрузка решения…</p></Section>;
  }
  if (isError) {
    return <Section title="Решение" subtitle={`#${id ?? "—"}`}><p className="memo" style={{ color: "var(--alert)" }}>Не удалось загрузить решение.</p></Section>;
  }
  if (!decision) {
    return <Section title="Решение" subtitle={`#${id ?? "—"}`}><p className="memo">Решение не найдено.</p></Section>;
  }

  const params = Object.entries(decision.params)
    .map(([key, value]) => `${key}: ${value}`)
    .join(" · ");

  return (
    <div className="flex flex-col gap-4">
      <Section title="Карточка решения" subtitle={decision.jira_key ?? `#${decision.id ?? "—"}`}>
        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Тип</dt><dd>{decision.type}</dd></div>
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Параметры</dt><dd className="mono">{params || "—"}</dd></div>
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Ответственный</dt><dd>{decision.owner}</dd></div>
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Задача</dt><dd className="mono">{decision.jira_key ?? "—"}</dd></div>
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Ожидаемый эффект</dt><dd className="mono">{formatByn(decision.expected_effect_byn)}</dd></div>
          <div><dt className="mono text-xs" style={{ color: "var(--muted)" }}>Вердикт</dt><dd>{decision.verdict}</dd></div>
        </dl>
        {decision.notes && <p className="memo serif mt-3">{decision.notes}</p>}
        <p className="mono mt-3 text-xs" style={{ color: "var(--muted)" }}>{notificationLabel(decision)}</p>
        {decision.jira_key && (
          <a className="tag mt-3 inline-flex" style={{ color: "var(--accent)" }} href={`/api/jira/${encodeURIComponent(decision.jira_key)}`} target="_blank" rel="noreferrer">
            Открыть задачу {decision.jira_key}
          </a>
        )}
      </Section>
      {decision.actual_effect_byn !== 0 && (
        <Section title="Фактический результат" subtitle={formatByn(decision.actual_effect_byn)}>
          <p className="memo">Результат сохранён в журнале. Полный снимок симуляции доступен после запуска «+14 дней» на главной странице.</p>
        </Section>
      )}
    </div>
  );
}
