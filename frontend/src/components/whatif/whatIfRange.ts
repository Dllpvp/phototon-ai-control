/** Диапазон What-If по смене №3 (§10.4 Readme.md).
 *  Конфигурация ползунка (границы и шаг) — не экономическое число:
 *  это диапазон, в котором API /api/whatif интерполирует по ANCHORS.
 */
export const OPS_MIN = 4;
export const OPS_MAX = 6;
export const OPS_STEP = 0.5;

/** Опорные точки anchors (4/5/6) для таблицы What-If. */
export const OPS_ANCHORS: readonly number[] = [4, 5, 6];
