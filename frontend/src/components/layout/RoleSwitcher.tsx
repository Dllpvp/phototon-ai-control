import { useQueryClient } from "@tanstack/react-query";
import { ChevronDown, User } from "lucide-react";

import type { DemoDept, DemoRole } from "../../api/types";
import { useDemoStore } from "../../store/demo";

const ROLES: { id: DemoRole; label: string }[] = [
  { id: "director", label: "Директор" },
  { id: "department_head", label: "Руководитель отдела" },
  { id: "production_head", label: "Производство" },
  { id: "hr_head", label: "HR" },
  { id: "finance_head", label: "Финансы" },
  { id: "support_head", label: "Клиенты и поддержка" },
  { id: "specialist", label: "Сотрудник" },
];

const DEPTS: { id: DemoDept; label: string }[] = [
  { id: "production", label: "Производство" },
  { id: "clients", label: "Клиенты" },
  { id: "hr", label: "HR" },
  { id: "finance", label: "Финансы" },
  { id: "logistics", label: "Логистика" },
  { id: "procurement", label: "Закупки" },
  { id: "admin", label: "Админ" },
];

export function RoleSwitcher() {
  const role = useDemoStore((s) => s.role);
  const dept = useDemoStore((s) => s.dept);
  const setRole = useDemoStore((s) => s.setRole);
  const setDept = useDemoStore((s) => s.setDept);
  const queryClient = useQueryClient();

  const handleRoleChange = (newRole: DemoRole) => {
    setRole(newRole);
    queryClient.invalidateQueries();
  };

  const handleDeptChange = (newDept: DemoDept) => {
    setDept(newDept);
    queryClient.invalidateQueries();
  };

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center gap-1 px-2 py-1 rounded border" style={{ borderColor: "var(--hair)", background: "var(--panel)" }}>
        <User size={14} style={{ color: "var(--muted)" }} />
        <select
          value={role}
          onChange={(e) => handleRoleChange(e.target.value as DemoRole)}
          className="mono text-xs bg-transparent border-none outline-none pr-4 appearance-none cursor-pointer"
          style={{ color: "var(--text)" }}
        >
          {ROLES.map((r) => (
            <option key={r.id} value={r.id}>
              {r.label}
            </option>
          ))}
        </select>
        <ChevronDown size={12} className="absolute right-1 pointer-events-none" style={{ color: "var(--muted)" }} />
      </div>

      {role === "department_head" && (
        <div className="relative flex items-center gap-1 px-2 py-1 rounded border animate-in fade-in slide-in-from-left-1" style={{ borderColor: "var(--hair)", background: "var(--panel)" }}>
          <select
            value={dept ?? ""}
            onChange={(e) => handleDeptChange(e.target.value as DemoDept)}
            className="mono text-xs bg-transparent border-none outline-none pr-4 appearance-none cursor-pointer"
            style={{ color: "var(--text)" }}
          >
            <option value="" disabled>Отдел...</option>
            {DEPTS.map((d) => (
              <option key={d.id} value={d.id}>
                {d.label}
              </option>
            ))}
          </select>
          <ChevronDown size={12} className="absolute right-1 pointer-events-none" style={{ color: "var(--muted)" }} />
        </div>
      )}
    </div>
  );
}
