import { useEffect } from "react";
import { Header } from "./components/layout/Header";
import { useThemeStore, applyThemeAttrs } from "./store/theme";

export default function App() {
  const { theme, mode } = useThemeStore();

  useEffect(() => {
    applyThemeAttrs(theme, mode);
  }, [theme, mode]);

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)", color: "var(--text)" }}>
      <Header />
      <main className="p-4">
        <p className="mono text-sm" style={{ color: "var(--muted)" }}>
          Каркас приложения. Данные появятся на этапе 5.
        </p>
      </main>
    </div>
  );
}
