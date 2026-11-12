import { Suspense, useEffect } from "react";
import { RouterProvider } from "react-router";

import { Header } from "./components/layout/Header";
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
      <Header />
      <main className="mx-auto max-w-6xl p-4">
        <Suspense fallback={<RouteFallback />}>
          <RouterProvider router={router} />
        </Suspense>
      </main>
      <ToastQueue />
    </div>
  );
}