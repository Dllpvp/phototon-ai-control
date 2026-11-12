import { adaptKpi } from "../lib/adapters";
import type { KpiDTO } from "../api/types";
import { describe, it, expect } from "vitest";

describe("adaptKpi", () => {
  it("должен корректно преобразовывать KpiDTO в KpiData", () => {
    const mockDto: KpiDTO = {
      node_id: "n1",
      name: "Продажи",
      value: 150000,
      unit: "BYN",
      status: "ok",
      // periods: undefined, // Проверяем только базовое преобразование
    };
    const result = adaptKpi(mockDto);

    expect(result.id).toBe("n1");
    expect(result.name).toBe("Продажи");
    expect(result.value).toBe(150000);
    expect(result.unit).toBe("BYN");
    expect(result.status).toBe("ok");
    expect(result.periods).toBeUndefined();
  });

  it("должен преобразовать статус 'hidden' в 'green'", () => {
    const mockDto: KpiDTO = {
      node_id: "n2",
      name: "Скрытый KPI",
      value: 10,
      unit: "unit",
      status: "hidden",
    };
    const result = adaptKpi(mockDto);
    expect(result.status).toBe("green");
  });
});