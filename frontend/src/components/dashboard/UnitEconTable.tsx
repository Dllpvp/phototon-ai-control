import { useUnitEcon } from "../../api/queries";
import { AsyncState } from "./AsyncState";

/** Таблица юнит-экономики (§7.8, §10.10).
 *  Выводит 5 строк (SKU/B2B) с разбивкой затрат и маржой.
 *  Маржа подсвечивается согласно статусу из DTO.
 */
export function UnitEconTable() {
  const query = useUnitEcon();

  return (
    <AsyncState query={query}>
      {(data) => (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-[10px] sm:text-xs mono">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--hair-strong)" }}>
                <th className="py-2 pr-2 font-medium" style={{ color: "var(--muted)" }}>
                  SKU / Клиент
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Цена
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Бум.
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Печ.
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Сб.
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Труд
                </th>
                <th className="py-2 px-1 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Брак
                </th>
                <th className="py-2 pl-2 text-right font-medium" style={{ color: "var(--muted)" }}>
                  Маржа
                </th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {data.map((row, i) => (
                <tr
                  key={row.sku}
                  style={{
                    borderBottom: i === data.length - 1 ? "none" : "1px solid var(--hair)",
                  }}
                >
                  <td className="py-2 pr-2 font-medium leading-tight" style={{ maxWidth: "80px" }}>
                    {row.sku}
                  </td>
                  <td className="py-2 px-1 text-right">{row.price.toFixed(0)}</td>
                  <td className="py-2 px-1 text-right">{row.paper.toFixed(0)}</td>
                  <td className="py-2 px-1 text-right">{row.printing.toFixed(0)}</td>
                  <td className="py-2 px-1 text-right">{row.binding.toFixed(0)}</td>
                  <td className="py-2 px-1 text-right">{row.labor.toFixed(0)}</td>
                  <td className="py-2 px-1 text-right">{row.defect.toFixed(0)}</td>
                  <td
                    className="py-2 pl-2 text-right font-bold"
                    style={{
                      color:
                        row.status === "red"
                          ? "var(--alert)"
                          : row.status === "yellow"
                            ? "var(--warn)"
                            : "var(--ok)",
                    }}
                  >
                    {row.margin_pct.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AsyncState>
  );
}
