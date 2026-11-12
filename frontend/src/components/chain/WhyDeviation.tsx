import { motion } from "framer-motion";
import { staggerList, fadeIn, useMotionReduced } from "../../lib/motion";

/**
 * Тип для причины отклонения
 */
type DeviationCause = {
  id: string;
  name: string;
  impact: number; // влияние в процентных пунктах (п.п.)
  domain: string; // домен: ERP, HR, Поддержка и т.д.
};

/**
 * Тип для waterfall данных
 */
type WaterfallData = {
  plan: number; // плановое значение
  fact: number; // фактическое значение
  causes: DeviationCause[]; // причины отклонения
};

/**
 * Пропсы для WhyDeviation
 */
type WhyDeviationProps = {
  data: WaterfallData;
};

/**
 * WhyDeviation — waterfall диаграмма "Почему отклонение".
 * Показывает: план → причины → факт.
 * Бары с подписями п.п.
 */
export function WhyDeviation({ data }: WhyDeviationProps) {
  const reduced = useMotionReduced();

  const { plan, fact, causes } = data;
  const deviation = fact - plan;

  // Вычисляем максимальное значение для нормализации высоты баров
  const allValues = [plan, fact, ...causes.map((c) => Math.abs(c.impact))];
  const maxValue = Math.max(...allValues);

  // Определяем тип бара
  const getBarType = (value: number, isPlanOrFact: boolean): string => {
    if (isPlanOrFact) return "neutral";
    return value >= 0 ? "positive" : "negative";
  };

  return (
    <motion.div
      className="glass-card"
      style={{ padding: "2rem" }}
    >
      {/* Заголовок */}
      <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text)", marginBottom: "1.5rem" }}>
        Почему отклонение
      </h3>

      {/* Waterfall диаграмма */}
      <motion.div
        className="waterfall"
        variants={reduced ? undefined : staggerList}
        initial="hidden"
        animate="show"
      >
        {/* План */}
        <motion.div
          className="waterfall-bar neutral"
          style={{ height: `${(plan / maxValue) * 100}%` }}
          variants={reduced ? undefined : fadeIn}
        >
          <div className="bar-value">{plan}</div>
          <div className="bar-label">План</div>
        </motion.div>

        {/* Причины отклонения */}
        {causes.map((cause, index) => {
          const barType = getBarType(cause.impact, false);
          const height = (Math.abs(cause.impact) / maxValue) * 100;

          return (
            <motion.div
              key={cause.id}
              className={`waterfall-bar ${barType}`}
              style={{ height: `${height}%` }}
              variants={reduced ? undefined : fadeIn}
              custom={index}
            >
              <div className="bar-value">
                {cause.impact > 0 ? "+" : ""}
                {cause.impact} п.п.
              </div>
              <div className="bar-label" style={{ fontSize: "0.65rem" }}>
                {cause.name}
              </div>
            </motion.div>
          );
        })}

        {/* Факт */}
        <motion.div
          className="waterfall-bar neutral"
          style={{ height: `${(fact / maxValue) * 100}%` }}
          variants={reduced ? undefined : fadeIn}
        >
          <div className="bar-value">{fact}</div>
          <div className="bar-label">Факт</div>
        </motion.div>
      </motion.div>

      {/* Итоговое отклонение */}
      <div
        style={{
          marginTop: "2rem",
          padding: "1rem",
          background: "var(--panel-2)",
          borderRadius: "var(--radius)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
          Итоговое отклонение:
        </span>
        <span
          style={{
            fontSize: "1.25rem",
            fontWeight: 700,
            fontFamily: "var(--font-mono)",
            color: deviation < 0 ? "var(--alert)" : "var(--ok)",
          }}
        >
          {deviation > 0 ? "+" : ""}
          {deviation} п.п.
        </span>
      </div>
    </motion.div>
  );
}