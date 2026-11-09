/** ChainPanel — панель цепочки с крошками и активным шагом (§10.6, T5.3). */
import { useMemo } from "react";
import { useChain, useSlice } from "../../api/queries";
import { AsyncState } from "../dashboard/AsyncState";
import { ChainBreadcrumbs } from "../graph/ChainBreadcrumbs";
import { ChainStep } from "../graph/ChainStep";

interface ChainPanelProps {
  selectedNodeId: string | null;
}

export function ChainPanel({ selectedNodeId }: ChainPanelProps) {
  const chainQuery = useChain(selectedNodeId);

  const sliceParams = useMemo(() => {
    const chain = chainQuery.data?.chain ?? [];
    if (!selectedNodeId || chain.length === 0) return null;
    const last = chain[chain.length - 1];
    return { from: "", to: "", line: last.node_id };
  }, [selectedNodeId, chainQuery.data?.chain]);

  const sliceQuery = useSlice(sliceParams);

  if (!selectedNodeId) {
    return (
      <div className="card" style={{ padding: "1rem" }}>
        <p className="memo text-sm" style={{ color: "var(--muted)" }}>
          Кликните по алерту, чтобы открыть цепочку
        </p>
      </div>
    );
  }

  return (
    <AsyncState
      query={chainQuery}
      isEmpty={(d) => !d || d.chain.length === 0}
      emptyText="Цепочка пуста"
      skeletonRows={3}
    >
      {(chainData) => (
        <div className="card" style={{ padding: "1rem" }}>
          <div className="flex items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <span className="display font-semibold" style={{ color: "var(--text)" }}>
                Цепочка причины
              </span>
              <span
                className="tag"
                style={{
                  color: chainData.source === "hint" ? "var(--ok)" : "var(--warn)",
                }}
              >
                {chainData.source === "hint" ? "hint" : "algorithm"}
              </span>
            </div>
          </div>

          <ChainBreadcrumbs chain={chainData.chain} activeNodeId={selectedNodeId} />

          <div className="mt-4">
            <ChainStep
              node={chainData.chain[chainData.chain.length - 1]}
              sliceQuery={sliceQuery}
              edgeNote={null}
            />
          </div>
        </div>
      )}
    </AsyncState>
  );
}