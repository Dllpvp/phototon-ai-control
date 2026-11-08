import type { ReactNode } from "react";

import { cn } from "../../lib/cn";

export interface SectionProps {
  title?: string;
  subtitle?: string | ReactNode;
  children: ReactNode;
  className?: string;
}

export function Section({ title, subtitle, children, className }: SectionProps) {
  return (
    <section className={cn("card", className)} style={{ padding: "1rem" }}>
      {(title || subtitle) && (
        <header className="mb-3 flex items-baseline justify-between gap-2">
          {title && (
            <h2 className="display text-lg font-semibold" style={{ color: "var(--text)" }}>
              {title}
            </h2>
          )}
          {subtitle && (
            <span className="mono text-xs" style={{ color: "var(--muted)" }}>
              {subtitle}
            </span>
          )}
        </header>
      )}
      {children}
    </section>
  );
}