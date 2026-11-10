import { useDecisions } from "../../api/queries";
import type { DecisionDTO } from "../../api/types";

export function JournalTable() {
  const query = useDecisions();
  if (query.isLoading) return <p className="memo">Загрузка журнала…</p>;
  if (query.isError) return <p className="memo" style={{ color: "var(--alert)" }}>Не удалось загрузить решения.</p>;
  if (!query.data?.length) return <p className="memo">Решений пока нет.</p>;
  return <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="mono" style={{ color: "var(--muted)" }}><th>Дата</th><th>Тип</th><th>Ответственный</th><th>Задача</th><th>Статус</th><th>Вердикт</th></tr></thead><tbody>{query.data.map((item: DecisionDTO) => <tr key={item.id ?? item.created_at} style={{ borderTop: "1px solid var(--hair)" }}><td className="mono">{item.created_at ? new Date(item.created_at).toLocaleDateString("ru-RU") : "—"}</td><td>{item.type}</td><td>{item.owner}</td><td><span className="tag mono">{item.jira_key ?? "—"}</span></td><td>{item.notification?.status ?? "—"}</td><td><span className="tag">{item.verdict === "pending" ? "ожидает" : item.verdict === "effective" ? "эффективно" : "неэффективно"}</span></td></tr>)}</tbody></table></div>;
}
