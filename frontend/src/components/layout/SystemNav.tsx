import { motion, AnimatePresence } from "framer-motion";
import { useQueryClient } from "@tanstack/react-query";
import { sharedAxis, spring, useMotionReduced } from "../../lib/motion";
import { useDemoStore, type DemoRole } from "../../store/demo";

type SystemTab = {
  id: string;
  label: string;
  role: DemoRole;
  dept: string | null;
};

const TABS: SystemTab[] = [
  { id: "overview", label: "Обзор", role: "director", dept: null },
  { id: "crm", label: "CRM", role: "support_head", dept: "clients" },
  { id: "support", label: "Поддержка", role: "support_head", dept: "clients" },
  { id: "erp", label: "ERP", role: "production_head", dept: "production" },
  { id: "1c", label: "1C", role: "finance_head", dept: "finance" },
  { id: "hr", label: "HR", role: "hr_head", dept: "hr" },
];

export function SystemNav() {
  const reduced = useMotionReduced();
  const queryClient = useQueryClient();
  const { currentTab, setCurrentTab, setRole, setDept } = useDemoStore();

  const handleTabChange = (tab: SystemTab) => {
    setCurrentTab(tab.id);
    setRole(tab.role);
    setDept(tab.dept);
    
    // Инвалидируем кэш, чтобы TanStack Query сделал refetch с новыми заголовками RBAC
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["chain"] });
  };

  const currentIndex = TABS.findIndex((t) => t.id === currentTab);

  return (
    <nav className="pill-nav" role="tablist" aria-label="Навигация по системам">
      {TABS.map((tab, index) => {
        const isActive = tab.id === currentTab;
        const direction = index > currentIndex ? 1 : -1;

        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            className={isActive ? "active" : ""}
            onClick={() => handleTabChange(tab)}
          >
            {isActive ? (
              <AnimatePresence mode="popLayout" initial={false}>
                <motion.span
                  key={tab.id}
                  custom={direction}
                  variants={reduced ? undefined : sharedAxis}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={spring.snappy}
                  style={{ display: "inline-block" }}
                >
                  {tab.label}
                </motion.span>
              </AnimatePresence>
            ) : (
              tab.label
            )}
          </button>
        );
      })}
    </nav>
  );
}