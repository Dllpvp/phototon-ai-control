/** LossCounter — накопленные потери с начала смены (§10.3, T5.2).
 *  Тик раз в секунду обновляет ТОЛЬКО цифры-одометры (framer-motion translateY),
 *  не перерисовывая секцию целиком. Значение loss_day приходит из DTO, не хардкод.
 */
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { formatByn } from "../../lib/format";

interface LossCounterProps {
  /** Потери за сутки (BYN/сут) — из DTO (node fin_loss_day). Если null/undefined — не рендеримся. */
  lossDay: number | null | undefined;
  /** ISO-datetime старта счётчика (dashboard.loss_counter_started_at). */
  startedAt: string;
}

const SECONDS_PER_DAY = 86400;
/** Сколько младших разрядов крутить одометром. */
const ODOMETER_DIGITS = 3;

/** Одна крутящаяся цифра: при смене значения старый символ уходит вниз, новый въезжает сверху. */
function OdometerDigit({ char }: { char: string }) {
  return (
    <span
      className="relative inline-block overflow-hidden text-center"
      style={{ width: "0.62em", height: "1em", verticalAlign: "baseline" }}
    >
      <AnimatePresence initial={false}>
        <motion.span
          key={char}
          initial={{ y: "-100%" }}
          animate={{ y: "0%" }}
          exit={{ y: "100%" }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {char}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}

/** Разбивает целое число на символы; помечает младшие разряды как анимируемые. */
function splitDigits(value: number): { char: string; animated: boolean }[] {
  const text = value.toLocaleString("ru-RU").replace(/[\u00A0\u202F]/g, " ");
  const chars = text.split("");
  const animateFrom = Math.max(0, chars.length - ODOMETER_DIGITS);
  return chars.map((char, index) => ({
    char,
    animated: index >= animateFrom && char >= "0" && char <= "9",
  }));
}

export function LossCounter({ lossDay, startedAt }: LossCounterProps) {
  const started = useMemo(() => new Date(startedAt).getTime(), [startedAt]);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  if (lossDay === null || lossDay === undefined) {
    return null;
  }

  const elapsed = Number.isFinite(started) ? Math.max(0, (now - started) / 1000) : 0;
  const lost = (lossDay * elapsed) / SECONDS_PER_DAY;
  const digits = splitDigits(Math.max(0, Math.floor(lost)));

  return (
    <div className="flex flex-col gap-1" style={{ minWidth: 0 }}>
      <div className="flex items-center gap-2">
        <span className="live-dot" />
        <span className="mono truncate text-xs" style={{ color: "var(--muted)" }}>
          LIVE TELEMETRY // L2-SHIFT-3
        </span>
      </div>
      <div
        className="mono text-4xl tabular-nums"
        style={{ color: "var(--alert)" }}
        aria-label={formatByn(lost)}
      >
        {digits.map((d, i) => (
          <span key={i}>{d.animated ? <OdometerDigit char={d.char} /> : d.char}</span>
        ))}
        <span className="ml-1 text-2xl">BYN</span>
      </div>
      <div className="mono truncate text-xs" style={{ color: "var(--muted)" }}>
        накопленные потери с начала недели 45 • 02.11.2026
      </div>
    </div>
  );
}
