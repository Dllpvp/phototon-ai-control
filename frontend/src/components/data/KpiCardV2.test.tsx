import { render, screen } from "@testing-library/react";
import { KpiCardV2 } from "./KpiCardV2";
import { describe, it, expect, vi } from "vitest";

// Мокаем framer-motion, чтобы не зависеть от анимаций в тестах
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

vi.mock("../../lib/motion", () => ({
  containerTransform: {},
  fadeIn: {},
  useMotionReduced: () => true,
}));

describe("KpiCardV2", () => {
  it("рендерит название, значение, единицу и статус", () => {
    const kpi = {
      id: "kpi-1",
      name: "Выручка",
      value: 123456,
      unit: "BYN",
      status: "ok" as const,
    };
    render(<KpiCardV2 kpi={kpi} />);

    expect(screen.getByText("Выручка")).toBeInTheDocument();
    expect(screen.getByText("123\u00A0456")).toBeInTheDocument(); // toLocaleString ru-RU
    expect(screen.getByText("BYN")).toBeInTheDocument();
    expect(screen.getByText("Норма")).toBeInTheDocument();
  });

  it("показывает 'Внимание' для статуса warn", () => {
    const kpi = {
      id: "kpi-2",
      name: "Маржа",
      value: 15,
      unit: "%",
      status: "warn" as const,
    };
    render(<KpiCardV2 kpi={kpi} />);
    expect(screen.getByText("Внимание")).toBeInTheDocument();
  });

  it("показывает 'Отклонение' для статуса red", () => {
    const kpi = {
      id: "kpi-3",
      name: "Проблема",
      value: -500,
      unit: "BYN",
      status: "red" as const,
    };
    render(<KpiCardV2 kpi={kpi} />);
    expect(screen.getByText("Отклонение")).toBeInTheDocument();
  });

  it("отображает плейсхолдер, если periods не загружены", () => {
    const kpi = {
      id: "kpi-4",
      name: "Тест",
      value: 100,
      unit: "шт",
      status: "ok" as const,
    };
    render(<KpiCardV2 kpi={kpi} />);
    expect(screen.getByText("Данные периодов не загружены")).toBeInTheDocument();
  });

  it("вызывает onClick при клике", () => {
    const handleClick = vi.fn();
    const kpi = {
      id: "kpi-5",
      name: "Клик",
      value: 1,
      unit: "раз",
      status: "ok" as const,
    };
    render(<KpiCardV2 kpi={kpi} onClick={handleClick} />);
    const card = screen.getByText("Клик").closest("div");
    if (card) {
      card.click();
      expect(handleClick).toHaveBeenCalledTimes(1);
    }
  });
});