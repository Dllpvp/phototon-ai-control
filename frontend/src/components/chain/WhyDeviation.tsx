import { motion } from "framer-motion";
import { staggerList, fadeIn, useMotionReduced } from "../../lib/motion";
import type { WhyDeviationVM } from "../../lib/adapters";

type WhyDeviationProps = {
  data: WhyDeviationVM;
};

export function WhyDeviation({ data }: WhyDeviationProps) {
  const reduced = useMotionReduced();
  const { plan, fact, causes, unit } = data;

  // Если данных нет — показываем пустое состояние
  if (fact === undefined || causes.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem" }}>
        <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>
          Почему отклонение
        </h3>
        <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
          Данные цепочки не загружены. Выберите KPI для анализа.
        </p>
      </div>
    );
  }

  const deviation = plan !== undefined ? fact - plan : 0;
  const allValues = [fact, ...(plan !== undefined ? [plan] : []), ...causes.map((c) => Math.abs(c.value))];
  const maxValue = Math.max(...allValues, 1);

  return (
    <div className="glass-card" style={{ padding: "2rem" }}>
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1.5rem" }}>
        Почему отклонение
      </h3>

      <motion.div className="waterfall" variants={reduced ? undefined : staggerList} initial="hidden" animate="show">
        {plan !== undefined && (
          <motion.div className="waterfall-bar neutral" style={{ height: `${(plan / maxValue) * 100}%` }} variants={reduced ? undefined : fadeIn}>
            <div className="bar-value">{plan} {unit}</div>
            <div className="bar-label">План</div>
          </motion.div>
        )}

        {causes.map((cause, index) => {
          const height = (Math.abs(cause.value) / maxValue) * 100;
          const barType = cause.value >= 0 ? "positive" : "negative";

          return (
            <motion.div
              key={cause.id}
              className={`waterfall-bar ${barType}`}
              style={{ height: `${height}%` }}
              variants={reduced ? undefined : fadeIn}
              custom={index}
            >
              <div className="bar-value" style={{ fontSize: "0.7rem" }}>
                {cause.value}
              </div>
              <div className="bar-label" style={{ fontSize: "0.65rem" }}>
                {cause.name}
              </div>
            </motion.div>
          );
        })}

        <motion.div className="waterfall-bar neutral" style={{ height: `${(fact / maxValue) * 100}%` }} variants={reduced ? undefined : fadeIn}>
          <div className="bar-value">{fact} {unit}</div>
          <div className="bar-label">Факт</div>
        </motion.div>
      </motion.div>

      {plan !== undefined && (
        <div style={{ marginTop: "2rem", padding: "1rem", background: "var(--panel-2)", borderRadius: "var(--radius)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "var(--muted)", fontSize: "0.875rem" }}>Итоговое отклонение:</span>
          <span style={{ fontSize: "1.25rem", fontWeight: 700, fontFamily: "var(--font-mono)", color: deviation < 0 ? "var(--alert)" : "var(--ok)" }}>
            {deviation > 0 ? "+" : ""}{deviation} {unit}
          </span>
        </div>
      )}
    </div>
  );
}