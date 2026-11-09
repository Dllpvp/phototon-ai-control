/** ChainBreadcrumbs — кликабельные крошки цепочки (§10.6, T5.3). */
import type { ChainNodeDTO } from "../../api/types";
import { useUIStore } from "../../store/ui";

interface ChainBreadcrumbsProps {
  chain: ChainNodeDTO[];
  activeNodeId?: string | null;
}

export function ChainBreadcrumbs({ chain, activeNodeId }: ChainBreadcrumbsProps) {
  const selectNode = useUIStore((s) => s.selectNode);

  if (!chain.length) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 text-xs mono" style={{ color: "var(--text)" }}>
      {chain.map((node, i) => (
        <span
          key={node.node_id}
          className="flex items-center gap-1.5"
          style={{ minWidth: 0 }}
        >
          {i > 0 && (
            <span style={{ color: "var(--muted)" }}>›</span>
          )}
          <button
            type="button"
            className="truncate flex items-center gap-1"
            style={{
              minWidth: 0,
              color: activeNodeId === node.node_id ? "var(--accent)" : "var(--text)",
              background: "transparent",
              border: "none",
              padding: "0.125rem 0.25rem",
              borderRadius: "var(--radius)",
              cursor: "pointer",
            }}
            onClick={() => selectNode(node.node_id)}
            title={node.name}
          >
            {node.name}
            {node.status === "red" && (
              <span className="tag" style={{ fontSize: "8px", color: "var(--alert)" }}>
                red
              </span>
            )}
            {node.status === "yellow" && (
              <span className="tag" style={{ fontSize: "8px", color: "var(--warn)" }}>
                yel
              </span>
            )}
            {i === chain.length - 1 && (
              <span className="tag" style={{ fontSize: "8px", color: "var(--ok)" }}>
                корень
              </span>
            )}
          </button>
        </span>
      ))}
    </div>
  );
}