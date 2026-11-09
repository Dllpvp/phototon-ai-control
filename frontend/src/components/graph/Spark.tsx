/** MiniSpark — мини-график (SVG, 14 дней) для среза данных (§10.6, T5.3). */
import { useMemo } from "react";
import { useSlice } from "../../api/queries";
import { useUIStore } from "../../store/ui";

interface SparkProps {
  nodeId: string;
  color?: string;
}

export function Spark({ nodeId, color = "var(--accent)" }: SparkProps) {
  const asOf = useUIStore((s) => s.as_of);
  
  // Без даты сценария нет воспроизводимого окна данных.
  const params = useMemo(() => {
    if (!asOf) return null;
    const to = new Date(`${asOf}T00:00:00Z`);
    if (Number.isNaN(to.getTime())) return null;
    const from = new Date(to);
    from.setUTCDate(from.getUTCDate() - 14);
    return {
      from: from.toISOString().slice(0, 10),
      to: to.toISOString().slice(0, 10),
    };
  }, [asOf]);

  const query = useSlice(params);
  const data = query.data;

  const points = useMemo(() => {
    if (!data || data.facts.length === 0) return "";
    
    // Фильтруем факты для нашего узла и сортируем по дате
    const nodeFacts = data.facts
      .filter((f) => f.metric === nodeId)
      .sort((a, b) => a.ts.localeCompare(b.ts));

    if (nodeFacts.length < 2) return "";

    const values = nodeFacts.map((f) => f.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    // SVG coords: 0,0 top-left; width=60, height=20
    const w = 60;
    const h = 20;
    const padding = 2;

    return nodeFacts
      .map((f, i) => {
        const x = (i / (nodeFacts.length - 1)) * w;
        const y = h - padding - ((f.value - min) / range) * (h - 2 * padding);
        return `${x},${y}`;
      })
      .join(" ");
  }, [data, nodeId]);

  if (query.isPending) return <div className="h-5 w-15 animate-pulse" style={{ background: "var(--panel-2)" }} />;
  if (query.isError || !points) return <div className="h-5 w-15" style={{ borderBottom: "1px dashed var(--muted)" }} />;

  return (
    <svg width="60" height="20" className="shrink-0 overflow-visible">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}
