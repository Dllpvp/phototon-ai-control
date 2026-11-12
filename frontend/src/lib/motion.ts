import type { Variants, Transition } from "framer-motion";
import { useReducedMotion } from "framer-motion";

/**
 * Material 3 / Android motion presets.
 * Все variants читают цвета из CSS-токенов (var(--токен)),
 * не из closure/пропсов.
 */

// ===== SPRING PRESETS =====
export const spring = {
  /** Стандартный Material 3 spring (раскрытие/сворачивание) */
  default: {
    type: "spring" as const,
    stiffness: 320,
    damping: 30,
  },
  /** Мягкий spring для stagger-появления */
  soft: {
    type: "spring" as const,
    stiffness: 260,
    damping: 24,
  },
  /** Быстрый spring для pill-nav переключения */
  snappy: {
    type: "spring" as const,
    stiffness: 400,
    damping: 28,
  },
};

// ===== ХУК: проверка prefers-reduced-motion =====
export function useMotionReduced(): boolean {
  return useReducedMotion() ?? false;
}

/**
 * Возвращает transition с учётом prefers-reduced-motion.
 * Если reduced-motion включён — transform-анимации отключаются,
 * остаётся только fade (opacity).
 */
export function getMotionTransition(
  reduced: boolean,
  base: Transition = spring.default,
): Transition {
  if (reduced) {
    return { type: "tween", duration: 0.15, ease: "easeOut" };
  }
  return base;
}

// ===== VARIANTS =====

/**
 * containerTransform — shared-element transition (Android).
 * Используется для раскрытия KpiCard → деталь (WhyDeviation + CauseCarousel).
 * Компонент должен иметь layoutId, передаваемый как пропс.
 */
export const containerTransform: Variants = {
  initial: { opacity: 0, scale: 0.96 },
  animate: {
    opacity: 1,
    scale: 1,
    transition: spring.default,
  },
  exit: {
    opacity: 0,
    scale: 0.96,
    transition: { duration: 0.2, ease: "easeInOut" },
  },
};

/**
 * sharedAxis (horizontal) — переключение SystemNav/вкладок.
 * slide + fade по горизонтали.
 */
export const sharedAxis: Variants = {
  initial: (direction: number = 1) => ({
    x: direction > 0 ? 40 : -40,
    opacity: 0,
  }),
  animate: {
    x: 0,
    opacity: 1,
    transition: spring.snappy,
  },
  exit: (direction: number = 1) => ({
    x: direction > 0 ? -40 : 40,
    opacity: 0,
    transition: { duration: 0.2, ease: "easeInOut" },
  }),
};

/**
 * fadeThrough — плавное появление/исчезновение (для CauseCarousel).
 * Используется с AnimatePresence mode="popLayout".
 */
export const fadeThrough: Variants = {
  initial: (direction: number = 1) => ({
    x: direction > 0 ? 40 : -40,
    opacity: 0,
  }),
  animate: {
    x: 0,
    opacity: 1,
    transition: spring.soft,
  },
  exit: (direction: number = 1) => ({
    x: direction > 0 ? -40 : 40,
    opacity: 0,
    transition: { duration: 0.18, ease: "easeInOut" },
  }),
};

/**
 * expandCollapse — accordion раскрытие (IndicatorsTable, RequiresDecision).
 * height:auto + opacity, spring.
 */
export const expandCollapse: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    overflow: "hidden",
  },
  expanded: {
    height: "auto",
    opacity: 1,
    overflow: "hidden",
    transition: spring.default,
  },
};

/**
 * staggerList — появление карточек KPI/stat.
 * Родитель использует staggerChildren, дети — fadeIn.
 */
export const staggerList: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.05,
    },
  },
};

/**
 * fadeIn — дочерний variant для staggerList.
 */
export const fadeIn: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: spring.soft,
  },
};

/**
 * fadeOnly — только fade, без transform.
 * Используется при prefers-reduced-motion.
 */
export const fadeOnly: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

/**
 * pulseAlert — пульсация LossCounter через токен --alert.
 * Цвет читается из CSS, не из пропса.
 */
export const pulseAlert: Variants = {
  pulse: {
    opacity: [1, 0.4, 1],
    transition: {
      duration: 1.2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// ===== УТИЛИТЫ ДЛЯ КОМПОНЕНТОВ =====

/**
 * Возвращает variants с учётом prefers-reduced-motion.
 * Если reduced-motion включён — transform отключается, остаётся fade.
 */
export function getVariantsWithReducedMotion(
  variants: Variants,
  reduced: boolean,
): Variants {
  if (!reduced) return variants;
  // При reduced-motion оставляем только opacity-анимации
  return {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.2 } },
    exit: { opacity: 0, transition: { duration: 0.15 } },
  };
}

/**
 * Direction helper для sharedAxis/fadeThrough.
 * Возвращает 1 или -1 в зависимости от индекса.
 */
export function getDirection(prevIndex: number, nextIndex: number): number {
  return nextIndex > prevIndex ? 1 : -1;
}

/**
 * LayoutId генератор для containerTransform.
 * Гарантирует уникальность layoutId для каждого KPI.
 */
export function getKpiLayoutId(kpiId: string, expanded: boolean): string {
  return expanded ? `kpi-detail-${kpiId}` : `kpi-card-${kpiId}`;
}