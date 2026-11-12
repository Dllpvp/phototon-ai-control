/** ChainStep — один шаг цепочки: название, срез + Spark(14 дней), note из ребра (§10.6). */
import type { ChainNodeDTO } from "../../api/types";
import { Spark } from "./Spark";
import { AsyncState } from "../dashboard/AsyncState";
import type { UseQueryResult } from "@tanstack/react-query";

interface ChainStepProps {
  node: ChainNodeDTO;
  sliceQuery?: UseQueryResult<{ facts: { metric: string; value: number }[] }, Error>;
  edgeNote?: string | null;
}

export function ChainStep({ node, sliceQuery, edgeNote }: ChainStepProps) {
  const data = sliceQuery?.data;
  const facts = data?.facts ?? [];
  const nodeFacts = facts.filter((f) => f.metric === node.node_id);

  const valueLine =
    node.status === "hidden" || node.value === null
      ? "скрыто"
      : `${node.value}${node.unit}`;

  return (
    <div className="card" style={{ padding: "1rem", border: "1px solid var(--hair)" }}>
      <header className="flex items-baseline justify-between gap-2 mb-2">
        <h2 className="display font-semibold" style={{ color: "var(--text)" }}>
          {node.name}
        </h2>
        <span
          className="mono text-xs"
          style={{
            color:
              node.status === "hidden"
                ? "var(--muted)"
                : node.status === "red"
                ? "var(--alert)"
                : node.status === "yellow"
                ? "var(--warn)"
                : "var(--ok)",
          }}
        >
          {valueLine}
        </span>
      </header>

      <div className="flex flex-wrap items-end gap-3 mb-2">
        <div style={{ minWidth: 0, flex: 1 }}>
          <span className="memo text-xs" style={{ color: "var(--muted)" }}>
            Срез
          </span>
          <AsyncState
            query={sliceQuery ?? ({} as UseQueryResult<{ facts: { metric: string; value: number }[] }, Error>)}
            isEmpty={(d) => d.facts.length === 0}
            emptyText="без фактов за окно"
            skeletonRows={2}
          >
            {() => (
              <div className="flex items-center gap-3">
                {nodeFacts.length ? (
                  <Spark nodeId={node.node_id} color="var(--accent)" />
                ) : (
                  <div className="h-5 w-15" style={{ borderBottom: "1px dashed var(--muted)" }} />
                )}
                <span className="mono text-sm tabular-nums" style={{ color: "var(--text)" }}>
                  {nodeFacts.length
                    ? `${nodeFacts.map((f) => f.value).join(" · ")}`
                    : "—"}
                </span>
              </div>
            )}
          </AsyncState>
        </div>

        <button
          type="button"
          className="tag"
          style={{ color: "var(--text)", cursor: "pointer" }}
        >
          показать
        </button>
      </div>

      {edgeNote ? (
        <p className="memo serif text-sm" style={{ color: "var(--muted)", margin: 0 }}>
          {edgeNote}
        </p>
      ) : null}
    </div>
  );
}