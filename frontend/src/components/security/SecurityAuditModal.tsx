/** Модалка журнала аудита LLM-вызовов (T9g). Только для роли director — backend вернёт 403 иначе. */
import { useState } from "react";

import { useSecurityAudit } from "../../api/queries";
import type { AuditDTO } from "../../api/types";
import { ApiError } from "../../api/client";
import { Modal } from "../layout/Modal";

export function SecurityAuditModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { data, isError, error, isLoading } = useSecurityAudit(10);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const isForbidden = error instanceof ApiError && error.status === 403;

  const state = isLoading ? "loading" : isError ? "error" : "success";
  const message = isForbidden
    ? "Доступ только для директора"
    : isError
      ? error.message
      : undefined;

  return (
    <Modal open={open} onClose={onClose} title="Журнал аудита LLM" state={state} message={message}>
      {!isError && data && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left" style={{ color: "var(--text)" }}>
            <thead>
              <tr className="mono text-xs" style={{ color: "var(--muted)" }}>
                <th className="pr-3 py-1">Время</th>
                <th className="pr-3 py-1">Бэкенд</th>
                <th className="pr-3 py-1">Маскировка</th>
                <th className="pr-3 py-1">Токены</th>
                <th className="pr-3 py-1">Вердикт</th>
                <th className="pr-3 py-1">SHA-256</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row: AuditDTO) => (
                <>
                  <tr
                    key={row.id}
                    className="cursor-pointer border-t"
                    style={{ borderColor: "var(--hair)" }}
                    onClick={() => setExpandedId(expandedId === row.id ? null : row.id)}
                  >
                    <td className="mono py-1 pr-3 text-xs" style={{ color: "var(--muted)" }}>{row.ts}</td>
                    <td className="mono py-1 pr-3 text-xs" style={{ color: "var(--muted)" }}>{row.backend}</td>
                    <td className="mono py-1 pr-3 text-xs" style={{ color: "var(--muted)" }}>{row.mask_level}</td>
                    <td className="mono py-1 pr-3 text-xs" style={{ color: "var(--muted)" }}>{row.tokens_count}</td>
                    <td className="mono py-1 pr-3 text-xs" style={{ color: row.verdict === "ok" ? "var(--ok)" : "var(--warn)" }}>{row.verdict}</td>
                    <td className="mono py-1 pr-3 text-xs" style={{ color: "var(--muted)" }}>{row.payload_sha256.slice(0, 16)}…</td>
                  </tr>
                  {expandedId === row.id && (
                    <tr key={`${row.id}-payload`} className="border-t" style={{ borderColor: "var(--hair)" }}>
                      <td colSpan={6} className="py-2 pr-3">
                        <pre
                          className="mono max-h-48 overflow-auto p-2 text-xs"
                          style={{ color: "var(--muted)", background: "var(--panel-2)", borderRadius: "var(--radius)" }}
                        >
                          {row.payload_masked_json}
                        </pre>
                        {row.reason && (
                          <p className="mono mt-1 text-xs" style={{ color: "var(--warn)" }}>
                            Причина: {row.reason}
                          </p>
                        )}
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!isError && data && data.length === 0 && (
        <p className="mono text-sm" style={{ color: "var(--muted)" }}>
          Пока нет записей аудита — вызовите ИИ-интерпретацию.
        </p>
      )}
    </Modal>
  );
}
