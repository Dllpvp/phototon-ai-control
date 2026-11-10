import { useEffect, useState, type FormEvent } from "react";

import { useCreateDecision, useDashboard } from "../../api/queries";
import type { DecisionCreateRequest, DecisionDTO } from "../../api/types";
import { Modal } from "../layout/Modal";
import { useToastStore } from "../layout/Toast";
import { useDemoStore } from "../../store/demo";
import { useUIStore } from "../../store/ui";

const OWNERS = ["Анна Петрова"] as const;

function today(): string {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function DecisionForm() {
  const open = useUIStore((state) => state.openDecisionForm);
  const close = useUIStore((state) => state.setOpenDecisionForm);
  const scenario = useUIStore((state) => state.scenario);
  const prefilled = useDemoStore((state) => state.prefilledDecision);
  const setPrefilled = useDemoStore((state) => state.setPrefilledDecision);
  const pushToast = useToastStore((state) => state.push);
  const dashboard = useDashboard(scenario);
  const createDecision = useCreateDecision();
  const [type, setType] = useState<DecisionCreateRequest["type"]>("hire");
  const [params, setParams] = useState('{"operators":1,"shift":3}');
  const [owner, setOwner] = useState<string>(OWNERS[0]);
  const [dueDate, setDueDate] = useState("");
  const [effect, setEffect] = useState("");
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    if (!open) return;
    setType(prefilled?.type ?? "hire");
    setParams(JSON.stringify(prefilled?.params ?? { operators: 1, shift: 3 }));
    setEffect(dashboard.data?.headline ?? "Эффект по прогнозу What-If");
    setDueDate((current) => current || (() => {
      const date = new Date();
      date.setDate(date.getDate() + 7);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    })());
    setPrefilled(null);
  }, [open, prefilled, setPrefilled, dashboard.data?.headline]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    let parsed: Record<string, number | string>;
    try {
      const value: unknown = JSON.parse(params);
      if (typeof value !== "object" || value === null || Array.isArray(value) || Object.keys(value).length === 0 ||
        Object.values(value).some((item) => typeof item !== "number" && typeof item !== "string")) {
        throw new Error("Параметры должны быть непустым объектом");
      }
      parsed = value as Record<string, number | string>;
    } catch {
      setValidationError("Укажите непустые числовые параметры в формате JSON.");
      return;
    }
    if (!dueDate || dueDate < today()) {
      setValidationError("Срок не может быть раньше сегодняшней даты.");
      return;
    }
    if (!effect.trim()) {
      setValidationError("Укажите ожидаемый эффект.");
      return;
    }
    setValidationError("");
    const request: DecisionCreateRequest = {
      scenario_id: scenario,
      type,
      params: parsed,
      owner,
      due_date: dueDate,
      expected_effect_byn: Number(effect.replace(/[^\d,.-]/g, "").replace(",", ".")) || 0,
      notes: notes.trim() || null,
      baseline_snapshot: null,
    };
    createDecision.mutate(request, {
      onSuccess: (decision: DecisionDTO) => {
        const telegramStatus = decision.notification?.status === "sent" ? "sent" : decision.notification?.status === "failed" ? "failed" : "skipped";
        pushToast({ kind: "success", text: `${decision.jira_key ?? "Решение"} создан · Telegram: ${telegramStatus}` });
        close(false);
      },
      onError: () => setValidationError("Не удалось оформить решение. Повторите попытку."),
    });
  };

  return (
    <Modal open={open} onClose={() => close(false)} title="Оформить решение" state={createDecision.isPending ? "loading" : validationError ? "error" : "success"} message={createDecision.isPending ? "Сохранение решения…" : undefined}>
      <form className="flex flex-col gap-3" onSubmit={submit}>
        <label className="flex flex-col gap-1">Тип<select className="card p-2" value={type} onChange={(event) => setType(event.target.value as DecisionCreateRequest["type"])}><option value="hire">Найм</option><option value="maintenance">Обслуживание</option><option value="other">Другое</option></select></label>
        <label className="flex flex-col gap-1">Параметры (JSON)<textarea className="card mono p-2" rows={2} value={params} onChange={(event) => setParams(event.target.value)} /></label>
        <label className="flex flex-col gap-1">Ответственный<select className="card p-2" value={owner} onChange={(event) => setOwner(event.target.value)}>{OWNERS.map((name) => <option key={name}>{name}</option>)}</select></label>
        <label className="flex flex-col gap-1">Срок<input className="card p-2" type="date" min={today()} value={dueDate} onChange={(event) => setDueDate(event.target.value)} /></label>
        <label className="flex flex-col gap-1">Ожидаемый эффект (BYN)<input className="card p-2" value={effect} onChange={(event) => setEffect(event.target.value)} /></label>
        <label className="flex flex-col gap-1">Примечание<textarea className="card p-2" maxLength={500} value={notes} onChange={(event) => setNotes(event.target.value)} /></label>
        {validationError && <p className="mono text-sm" style={{ color: "var(--alert)" }}>{validationError}</p>}
        <div className="flex justify-end gap-2"><button type="button" className="tag" onClick={() => close(false)}>Отмена</button><button className="tag" style={{ color: "var(--accent)" }} disabled={createDecision.isPending || !params.trim() || !dueDate || dueDate < today() || !effect.trim() || notes.length > 500}>Оформить</button></div>
      </form>
    </Modal>
  );
}
