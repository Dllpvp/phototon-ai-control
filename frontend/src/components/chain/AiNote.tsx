/** AiNote — кнопка «Объяснить» и пояснение ИИ с бейджем источника (§10.6, T5.3b). */
import type { AiDTO, ChainNodeDTO, ScenarioId } from "../../api/types";
import { useAi } from "../../api/queries";

interface AiNoteProps {
  scene: ScenarioId;
  chain: ChainNodeDTO[];
}

const SOURCE_LABEL: Record<AiDTO["source"], string> = {
  cache: "кэш",
  deepseek: "ИИ",
  fallback: "шаблон",
};

export function AiNote({ scene, chain }: AiNoteProps) {
  const ai = useAi();
  const last = chain[chain.length - 1];

  if (!last) return null;

  const explain = () => {
    const delta: Record<string, number> = {};
    for (const node of chain) {
      if (node.delta_from_parent !== null) delta[node.node_id] = node.delta_from_parent;
    }
    ai.mutate({
      scene,
      node_id: chain[0].node_id,
      chain: chain.map((n) => n.node_id),
      delta,
      cost_per_day: chain[0].cost_per_day ?? 0,
    });
  };

  return (
    <div className="flex flex-col gap-2">
      <button
        type="button"
        className="tag"
        onClick={explain}
        disabled={ai.isPending}
        style={{ color: "var(--accent)", cursor: ai.isPending ? "wait" : "pointer", alignSelf: "flex-start" }}
      >
        {ai.isPending ? "Анализируем…" : "Объяснить"}
      </button>

      {ai.isError && (
        <p className="memo text-sm" style={{ color: "var(--alert)" }}>
          Не удалось получить пояснение. Попробуйте ещё раз.
        </p>
      )}

      {ai.data && (
        <div className="memo" style={{ padding: "0.75rem" }}>
          <p className="serif text-sm" style={{ color: "var(--text)" }}>
            {ai.data.interpretation}
          </p>
          <span className="tag mt-2" style={{ color: "var(--muted)" }}>
            {SOURCE_LABEL[ai.data.source]}
          </span>
        </div>
      )}
    </div>
  );
}
