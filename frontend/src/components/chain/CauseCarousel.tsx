import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fadeThrough, getDirection, useMotionReduced } from "../../lib/motion";

/**
 * Тип для причины отклонения
 */
export type Cause = {
  id: string;
  name: string;
  impact: number; // вклад в отклонение, %
  domain: "ERP" | "HR" | "Поддержка" | "CRM" | "1C" | "Другое";
  description?: string;
};

/**
 * Пропсы для CauseCarousel
 */
type CauseCarouselProps = {
  causes: Cause[];
  onPrefillDecision?: (cause: Cause) => void;
};

/**
 * Цвет тега домена — через токены, не hex
 */
const DOMAIN_TAG_CLASS: Record<Cause["domain"], string> = {
  ERP: "badge-accent",
  HR: "badge-warn",
  Поддержка: "badge-alert",
  CRM: "badge-ok",
  "1C": "badge-accent",
  Другое: "badge-warn",
};

/**
 * CauseCarousel — жёлтая карточка «Причина N из M».
 * Большой %, теги доменов, стрелки, «Оформить решение».
 */
export function CauseCarousel({ causes, onPrefillDecision }: CauseCarouselProps) {
  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const reduced = useMotionReduced();

  if (causes.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <p style={{ color: "var(--muted)" }}>Причины отклонения не найдены</p>
      </div>
    );
  }

  const current = causes[index];
  const isLast = index === causes.length - 1;
  const isFirst = index === 0;

  const goNext = () => {
    if (isLast) return;
    setDirection(1);
    setIndex((i) => i + 1);
  };

  const goPrev = () => {
    if (isFirst) return;
    setDirection(-1);
    setIndex((i) => i - 1);
  };

  const handleDecision = () => {
    if (onPrefillDecision) {
      onPrefillDecision(current);
    }
  };

  return (
    <div className="accent-card">
      {/* Счётчик N из M */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
          position: "relative",
          zIndex: 1,
        }}
      >
        <span
          style={{
            fontSize: "0.875rem",
            fontWeight: 600,
            color: "var(--text)",
            fontFamily: "var(--font-mono)",
          }}
        >
          Причина {index + 1} из {causes.length}
        </span>

        {/* Стрелки навигации */}
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={goPrev}
            disabled={isFirst}
            style={{
              background: "rgba(255, 255, 255, 0.2)",
              border: "1px solid rgba(255, 255, 255, 0.3)",
              borderRadius: "var(--radius)",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: isFirst ? "not-allowed" : "pointer",
              opacity: isFirst ? 0.4 : 1,
              color: "var(--text)",
              fontSize: "1rem",
            }}
            aria-label="Предыдущая причина"
          >
            ‹
          </button>
          <button
            onClick={goNext}
            disabled={isLast}
            style={{
              background: "rgba(255, 255, 255, 0.2)",
              border: "1px solid rgba(255, 255, 255, 0.3)",
              borderRadius: "var(--radius)",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: isLast ? "not-allowed" : "pointer",
              opacity: isLast ? 0.4 : 1,
              color: "var(--text)",
              fontSize: "1rem",
            }}
            aria-label="Следующая причина"
          >
            ›
          </button>
        </div>
      </div>

      {/* Контент причины с анимацией slide */}
      <div style={{ position: "relative", zIndex: 1, minHeight: "180px" }}>
        <AnimatePresence mode="popLayout" custom={direction}>
          <motion.div
            key={current.id}
            custom={direction}
            variants={reduced ? undefined : fadeThrough}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={reduced ? { duration: 0.15 } : undefined}
            style={{ position: "absolute", top: 0, left: 0, right: 0 }}
          >
            {/* Большой % вклада */}
            <div className="big-percent">
              {Math.abs(current.impact)}%
            </div>

            {/* Название причины */}
            <h4
              style={{
                fontSize: "1.25rem",
                fontWeight: 700,
                marginTop: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              {current.name}
            </h4>

            {/* Описание */}
            {current.description && (
              <p
                style={{
                  fontSize: "0.875rem",
                  color: "var(--muted)",
                  marginBottom: "1rem",
                  lineHeight: 1.5,
                }}
              >
                {current.description}
              </p>
            )}

            {/* Тег домена */}
            <span className={`badge ${DOMAIN_TAG_CLASS[current.domain]}`}>
              {current.domain}
            </span>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Кнопка «Оформить решение» */}
      <button
        onClick={handleDecision}
        style={{
          position: "relative",
          zIndex: 1,
          marginTop: "1.5rem",
          width: "100%",
          padding: "0.75rem",
          background: "var(--text)",
          color: "var(--accent)",
          border: "none",
          borderRadius: "var(--radius)",
          fontWeight: 700,
          fontSize: "0.875rem",
          cursor: "pointer",
          transition: "all 0.2s ease",
        }}
        onMouseEnter={(e) => {
          if (!reduced) {
            (e.target as HTMLButtonElement).style.transform = "translateY(-1px)";
          }
        }}
        onMouseLeave={(e) => {
          if (!reduced) {
            (e.target as HTMLButtonElement).style.transform = "translateY(0)";
          }
        }}
      >
        Оформить решение
      </button>
    </div>
  );
}