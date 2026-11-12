import { Suspense, useEffect } from "react";
import { RouterProvider } from "react-router";

import { Section } from "./components/layout/Section";
import { ToastQueue } from "./components/layout/Toast";
import { applyThemeAttrs, useThemeStore } from "./store/theme";
import { router } from "./routes";

function RouteFallback() {
  return (
    <Section title="Загрузка" subtitle="/">
      <p className="mono text-sm" style={{ color: "var(--muted)" }}>
        Загрузка страницы…
      </p>
    </Section>
  );
}

export default function App() {
  const { theme, mode } = useThemeStore();

  useEffect(() => {
    applyThemeAttrs(theme, mode);
  }, [theme, mode]);

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)", color: "var(--text)" }}>
      <main className="mx-auto w-full p-0">
        <Suspense fallback={<RouteFallback />}>
          <RouterProvider router={router} />
        </Suspense>
      </main>
      <ToastQueue />
    </div>
  );
}