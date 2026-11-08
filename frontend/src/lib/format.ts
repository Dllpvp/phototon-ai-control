/** Форматтеры для UI (§10.2). Только отображение — без экономических расчётов. */

/** Нормализует узкие/неразрывные пробелы Intl в обычный пробел (как в ответах API). */
function normalizeSpaces(s: string): string {
  return s.replace(/[\u00A0\u202F]/g, " ");
}

/** Форматирует сумму в BYN (ru-RU). */
export function formatByn(value: number): string {
  const n = new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
  return `${normalizeSpaces(n)} BYN`;
}

/** Форматирует проценты с одним знаком: 32 → "32,0%". */
export function formatPct(value: number): string {
  const n = new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
  return `${normalizeSpaces(n)}%`;
}

/** Форматирует дату как "02.11.2026" (ru-RU). */
export function formatDate(dateStr: string | Date): string {
  const date = typeof dateStr === "string" ? new Date(dateStr) : dateStr;
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

/** Склонение существительного: pluralize(23, ["заказ","заказа","заказов"]) → "заказа". */
export function pluralize(n: number, forms: [string, string, string]): string {
  const mod10 = Math.abs(n) % 10;
  const mod100 = Math.abs(n) % 100;
  if (mod10 === 1 && mod100 !== 11) return forms[0];
  if (mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)) return forms[1];
  return forms[2];
}