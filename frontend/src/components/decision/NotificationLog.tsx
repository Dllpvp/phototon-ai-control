import { useNotifications } from "../../api/queries";
import type { NotificationDTO } from "../../api/types";

export function NotificationLog() {
  const query = useNotifications();
  if (query.isLoading) return <p className="memo">Загрузка отправок…</p>;
  if (query.isError) return <p className="memo" style={{ color: "var(--alert)" }}>Не удалось загрузить журнал отправок.</p>;
  if (!query.data?.length) return <p className="memo">Отправок пока нет.</p>;
  return <div className="flex flex-col">{query.data.map((item: NotificationDTO) => <article className="flex flex-wrap items-start justify-between gap-2 py-3" style={{ borderBottom: "1px solid var(--hair)" }} key={item.id}><div><span className="tag">{item.status === "sent" ? "Отправлено" : item.status === "failed" ? "Ошибка" : "Пропущено: нет токена"}</span><p className="mt-1 text-sm">{item.body || item.subject}</p></div><time className="mono text-xs" style={{ color: "var(--muted)" }}>{new Date(item.created_at).toLocaleString("ru-RU")}</time></article>)}</div>;
}
