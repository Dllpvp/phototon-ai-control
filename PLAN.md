# PLAN.md — исполняемый план проекта «Фотопринт·Контроль» для AI-агента
Версия 1.0 · 06.11.2026 · Источник правды по смыслу и цифрам: Readme.md (§N). Правила поведения: AGENTS.md. Этот файл — очередь задач и приёмка.

## 0. Инструкция агенту (читать первым)
1. Ты — агент-исполнитель хакатон-проекта. Ролей нет, есть очередь задач.
2. Цикл по задаче: прочитать задачу → писать ТОЛЬКО файлы из блока ФАЙЛЫ → выполнить команды ПРИЁМКИ → если всё зелёное: поставить [x], дописать строку в LOG (§5), сделать коммит (§6) → перейти к следующей задаче.
3. Порядок задач не менять (зависимости). Задачи с [x] не переписывать «для красоты».
4. Красный тест = задача НЕ выполнена. Не коммитить красное.
5. Если приёмка противоречит Readme.md — Readme.md главнее; противоречие описать в теле коммита и продолжить.
6. Любой числовой вывод на экран — только из backend/app/core/ (ANCHORS/CONSTANTS). Хардкод экономических чисел в frontend/src — блокирующий дефект (проверка: grep пуст, §задачи B2).
7. Новые зависимости — запрещено без записи в docs/adr/.
8. Контекст держи малым: одна задача = один блок файлов; файл ≤ 300 строк; без `any` в TS.

## 1. Контекст-выжимка (чтобы не перечитывать всё)
- Продукт: управленческий MVP фабрики фотокниг. Петля: видит отклонение → причина в BYN → решение → доставка (Jira-мок + Telegram) → проверка «было→стало» (+14 дней) → негативная ветка-коррекция.
- Слои (не перепрыгивать): data/*.json → app/core/ (чистая математика, без FastAPI) → app/api/ (тонкие роутеры, DTO in/out) → frontend (только отрисовка).
- Стек: Python 3.12 (pin, ADR-0001; НЕ 3.14), FastAPI+Pydantic v2+uvicorn, uv; SQLite (журнал); React 19+TS+Vite+Tailwind v4+Recharts+zustand+TanStack Query+framer-motion; reportlab (PDF, DejaVu); OpenAI SDK (DeepSeek через klinch cloud), httpx (Telegram); pytest+httpx AsyncClient.
- Инварианты (не ломать никогда):
  * ANCHORS what-if: ops 4→(downtime 14, sla 23, revenue 41200, loss 1840); 5→(8,11,44900,980); 6→(2,3,47600,260).
  * effect_14d = (1840−260)×14 = 22120; defect now/after/neg = 9/4/11; loss_neg = 2170.
  * peak(47): forecast 1240, capacity 1050, deficit 190 (≈2 оператора), downtime 9 ч, loss 1180 BYN/сут.
  * Константы: COST_PER_DOWNTIME_H=131.0; BASE_WEEKLY_ORDERS=917.0; TREND_PER_WEEK=0.002; BASELINE_WEEK=45; ORDERS_PER_OPERATOR_WEEK=175; REPRINT_COST=510; LAMINATION_SERVICE_COST=4200.
  * Граф: 18 узлов, 17 рёбер, DAG; chain_main = [fin_margin, sales_sla_breach, prod_downtime_l2, hr_operators_s3]; ребро hr→downtime: weight 3.0, curvature 0.75.
  * impact (§7.3): d_to = d*weight*sign + curvature*copysign(d*d, d); depth ≤ 6.
  * forecast (§7.6): base = 917*(1+0.002*(w−45)); forecast = round(base*coeff, -1).
- Палитра (§10.1): --bg #0B0F14; --panel #121821; --border #1E293B; --text #E5EDF5; --muted #94A3B8; --red #EF4444; --amber #F59E0B; --green #22C55E; --accent #38BDF8; --accent-2 #A855F7; цифры tabular-nums; шрифт Inter.
- Язык: UI/тексты/сообщения — русский; код — английский; валюта BYN; даты ru-RU.

## 2. УЖЕ ГОТОВО (не пересоздавать; правка — только багфикс-задачей)
Этап 0: скаффолд репо (структура §4.2), pyproject (python pin 3.12), vite+react+ts+tailwind, /api/health, AGENTS.md, .env.example, .gitignore, git+GitHub, polars[rtcompat], Node 22.
Этап 1: core/constants.py (7 констант); core/anchors.py (+validate_anchors); data/graph.json (18/17 + path_hints + root_causes); data/norms.json (8 метрик); data/seasonality.json; app/data/scenarios/{main,neg,peak}.json; app/data/seed.py → data/facts.json (50 фактов, seed=42, SHA256 стабилен); core/loader.py; app/dependencies.py (lru_cache); tests/test_anchors.py, tests/test_graph.py.
Этап 2: core/impact.py (delta); core/interpolation.py (interp, clamping); core/economics.py (loss_day); core/forecast.py (ForecastResult); core/simulate.py (simulate, SimResult, branch main/neg); tests/test_impact/interpolation/forecast/economics/simulate.
Текущий статус: `uv run pytest -q` → 49 passed, warnings 0.

## 3. Очередь задач

### ЭТАП 3 — API и интеграции (06.11)
- [x] **A1 · DTO + read-only эндпоинты** (§9.1–9.3; T3.1–T3.5)
  ФАЙЛЫ: создать backend/app/schemas.py; backend/app/api/{dashboard,graph,slices,whatif,forecast,unit_econ}.py; backend/tests/test_api.py; править backend/app/main.py (роутеры prefix=/api, глобальный Exception→500 {detail}).
  ПРИЁМКА:
  1) schemas.py: Norm, GraphNode, GraphEdge, Snapshot (§9.1) + KpiDTO, AlertDTO, SlicDescDTO, DashboardDTO, ChainDTO, SliceDTO, WhatIfDTO, WhatIfDeltaDTO, RecommendedDTO, ForecastDTO, UnitEconDTO (§9.3); поля дословно из Readme, без выдумывания.
  2) Эндпоинты: GET /api/snapshot; GET /api/dashboard; GET /api/chain/{node_id}; GET /api/slice; POST /api/whatif; GET /api/forecast; GET /api/unit-economics.
  3) /api/dashboard: alerts отсортированы по cost_per_day DESC; loss_counter_started_at ISO; headline == «Маржа −10 п.п., −1 840 BYN/сут».
  4) /api/chain/fin_margin: 4 узла, последний hr_operators_s3, source=="hint".
  5) POST /api/whatif value=99 → 400 {detail} (ничего не падает, §9.4).
  6) Тесты: test_whatif_anchor_points (4/5/6 → кортежи из §1 инвариантов); test_dashboard; test_chain; test_bad_input.
  7) `uv run pytest -q` зелёный (ожидание ≥55 passed).
  НЕ ДЕЛАТЬ: decisions/telegram/jira/ai/pdf; frontend; core/.
  ПРОВЕРКА: pytest; uvicorn → /docs прокликать whatif(5)→(8,11,44900,980), chain, forecast, unit-economics.
  КОММИТ: feat(api): DTO + read-only endpoints (stage 3.1)

- [x] **A2 · Решения + SQLite + Jira-мок + Telegram** (§9.2, §11.1–11.2; T3.6–T3.7)
  ФАЙЛЫ: создать backend/app/db.py; backend/app/api/{decisions,jira_mock,notifications}.py; backend/app/integrations/{jira,telegram}.py; backend/tests/test_telegram.py; править main.py, tests/test_api.py.
  ПРИЁМКА:
  1) state.db (gitignored): таблицы decisions, jira_counter (старт 1234), notifications; init при старте.
  2) POST /api/decisions → 200 {decision_id, jira_key=="PROD-1234", notification{status}}; status ∈ {sent, skipped_no_token, failed}.
  3) GET /api/decisions; GET /api/decisions/{id} (+notification).
  4) POST /api/decisions/{id}/simulate {days:14, branch:"main"|"neg"} → SimulationDTO; main: verdict=="effective", |effect−22120|≤1; neg: verdict=="ineffective", compensating_cause=="equip_lamination_wear"; actual_effect/verdict пишутся в БД.
  5) GET /api/jira/PROD-1234 → 200 (поля решения + url).
  6) telegram.send_message: нет токена ИЛИ OFFLINE_MODE → skipped_no_token; сетевая ошибка/не-200 → failed; 200 → sent; timeout 3 c; исключение НЕ уходит выше.
  7) Тесты: test_create_decision; test_jira; test_telegram_off; test_simulate_endpoint. pytest зелёный.
  НЕ ДЕЛАТЬ: ai/pdf; frontend; webhook/polling-бот (только исходящий sendMessage).
  КОММИТ: feat(api): decisions + sqlite + jira + telegram (stage 3.2)

- [x] **A3 · AI с анти-галлюцинацией + Executive PDF** (§11.3–11.4; T3.8–T3.10)
  ФАЙЛЫ: создать backend/app/integrations/ai.py; backend/app/api/ai.py; backend/app/report/{context,pdf}.py; backend/app/api/report.py; backend/app/report/fonts/DejaVuSans.ttf + DejaVuSans-Bold.ttf (ЗАКОММИТИТЬ); backend/tests/test_ai_guard.py; править tests/test_api.py (test_pdf, test_ai_health), main.py.
  ПРИЁМКА:
  1) ai.interpret(ctx): ключ sha256(json(ctx,sort_keys)) → кэш data/ai_cache.json; hit → source="cache"; offline/AI_ENABLED=false → fallback source="fallback"; online: OpenAI SDK, temperature=0, response_format, timeout 5 → validate → ok: source="deepseek", иначе fallback + reason.
  2) validate(raw,ctx): числа/сущности вне whitelist ctx → (False, reason с токеном). Тест: ctx={"margin":32,"cost":1840}, raw.interpretation="маржа 99%" → ok==False и "99" in reason.
  3) GET /api/ai/health → {enabled, model, cache_size}.
  4) pdf.py: reportlab platypus, A4, DejaVuSans (кириллица); блоки: топ-3 отклонения+причины, cost of inaction, решения (owner/due/verdict), «было→стало»; GET /api/report/executive.pdf?scenario=main → 200 application/pdf; bytes startswith b"%PDF-1.4"; текст содержит «Маржинальность».
  5) `uv run pytest -q` зелёный (ожидание ≥60 passed).
  НЕ ДЕЛАТЬ: frontend; SDK DeepSeek (только OpenAI SDK); оставлять ttf вне репо.
  ПРОВЕРКА: pytest; скачать PDF из /docs и открыть — кириллица читается.
  КОММИТ: feat(api): AI guard + exec pdf (stage 3.3)

  **GATE G1 (конец Этапа 3):** pytest ≥60 passed; в /docs все эндпоинты §9.2 отвечают 200/400-по-правилу; PDF открывается; POST /api/decisions даёт PROD-1234. Бэкенд ПОЛНОСТЬЮ готов.

### ЭТАП 4 — UI-каркас (07.11)
- [x] **B1 · types/api-слой/сторы/layout/тема** (§4.2, §10.1; T4.1–T4.5)
  ФАЙЛЫ: frontend/vite.config.ts (proxy /api→http://127.0.0.1:8000); src/api/{types,client,queries}.ts; src/store/{ui,demo}.ts; src/lib/{format,cn}.ts; src/styles/theme.css; src/components/layout/{Header,Section,Modal,Toast,DemoBadge}.tsx; src/pages/Dashboard.tsx (скелет секций); src/{App,routes,main}.tsx.
  ПРИЁМКА:
  1) types.ts — зеркало schemas.py; ни одного `any`.
  2) theme.css — палитра из §1 точно; цифры tabular-nums.
  3) Header: лого «Фотопринт·Контроль»; сценарий [main▾]; кнопки «Сброс демо», «Оформить», «⏩ +14 дней», «PDF»; подпись «неделя 45 · 02.11.2026».
  4) Каждая секция-заглушка имеет loading/error/empty (skeleton/сообщение) — без белых мигающих экранов.
  5) `npm run build` без TS-ошибок; `npm run dev` открывает каркас.
  НЕ ДЕЛАТЬ: реальные KPI/графики/ползунок; любые экономические числа во фронте.
  КОММИТ: feat(ui): shell, theme, api layer, stores (stage 4)

### ЭТАП 5 — UI-данные (07.11)
- [ ] **B2 · KPI, алерты, LossCounter, ChainPanel, AiNote(база), GraphView** (§10.2–10.3, §10.6; T5.1–T5.3)
  ФАЙЛЫ: src/components/data/{KpiCard,AlertRow,MiniSpark,ChartBox,LossCounter}.tsx; src/components/graph/{ChainBreadcrumbs,ChainStep,GraphView}.tsx; src/components/ai/AiNote.tsx; править src/pages/Dashboard.tsx.
  ПРИЁМКА:
  1) KpiGrid columns=4, 12 KPI из useDashboard().kpis; цвета статусов из палитры.
  2) AlertsColumn в порядке ответа API; клик AlertRow → store.ui выбранный узел + кросс-фильтр slice (week/line/shift из AlertDTO.slice).
  3) LossCounter: клиентский тик 1 р/с от loss_counter_started_at; lost = loss_day*(now−started)/86400; перерисовывается только <span>; пульс на red; «Сброс демо» обнуляет; время НЕ считается на бэке.
  4) ChainPanel(fin_margin): breadcrumbs 4 шага до «Нехватка 2 брошюровщиков №3»; клик шага → срез (useSlice) + MiniSpark(14 дн) + note ребра; справа AiNote: кнопка «Объяснить» → POST /api/ai/interpret; состояния loading/cache/fallback; подпись «сгенерировано ИИ по фактам системы».
  5) GraphView: читаемый SVG узлов/рёбер, подсветка соседей 1-hop при hover, без редактора.
  6) `npm run build` зелёный; `grep -rE "1840|41200|22120|980|260" frontend/src` → ПУСТО.
  НЕ ДЕЛАТЬ: backend; WhatIf/Forecast/UnitEcon; вычисления в компонентах (только форматирование DTO).
  КОММИТ: feat(ui): kpi + loss counter + chain (stage 5.1)

- [ ] **B3 · WhatIf + ForecastCard + UnitEconTable** (§10.4, §10.9, §7.8; T5.4–T5.6)
  ФАЙЛЫ: src/components/whatif/{WhatIfSlider,WhatIfTable,WhatIfDeltaCards}.tsx; src/components/forecast/ForecastCard.tsx; src/components/econ/UnitEconTable.tsx; править Dashboard.tsx.
  ПРИЁМКА:
  1) Slider 4..6 шаг 0.5, дефолт 4; отпускание → debounce 120 мс → useWhatIf(value); таблица 3 строки (4/5/6) × 4 столбца = якоря §1; текущая строка подсвечена; WhatIfDeltaCards из vs_now.
  2) «Принять как решение» → store.demo.prefilledDecision {type:"hire", params:{operators: value−4, shift:3}} + скролл к форме.
  3) ForecastCard: «Пик через 14 дней (неделя 47): 1 240 заказов при мощности 1 050»; дефицит 190 → подпись «≈ 2 оператора»; простой 9 ч/сут; потери 1 180 BYN/сут; кнопки «Прогнать сценарий» (whatif ops=6) и «Принять превентивное решение».
  4) UnitEconTable: 5 строк §7.8 (цена/бумага/печать/брошюровка/кадры/брак/маржа%); строка «B2B клиент №7» (маржа −1.9) подсвечена red.
  5) build зелёный; grep хардкода пуст.
  НЕ ДЕЛАТЬ: backend; интерполяция во фронте (только через API→core).
  КОММИТ: feat(ui): whatif + forecast + unit econ (stage 5.2)

  **GATE G2:** build зелёный; руками пройти шаги 2–5 и 9 демо-трека (§16.2) в UI; grep пуст.

### ЭТАП 6 — Петля решений (08.11)
- [ ] **C1 · DecisionForm, Journal, NotificationLog, BeforeAfter, NegativeBranch, DecisionPage** (§10.5, §10.7–10.8; T6.1–T6.5)
  ФАЙЛЫ: src/components/decision/{DecisionForm,JournalTable,NotificationLog}.tsx; src/components/simulate/{BeforeAfterCard,NegativeBranch}.tsx; src/pages/{DecisionPage,JournalPage}.tsx; править Dashboard.tsx (JournalTable + кнопки header).
  ПРИЁМКА:
  1) DecisionForm: поля/дефолты/валидации §10.5; prefill из what-if; «Оформить» → POST /api/decisions → Toast «PROD-1234» + статус Telegram.
  2) JournalTable: бейджи verdict (effective=green, ineffective=red, pending=muted); клик строки → /decision/:id.
  3) «⏩ +14 дней» → POST /api/decisions/{id}/simulate branch=main → BeforeAfterCard: «Было: брак 9% · простой 14 ч · потери 1 840 BYN/сут / Стало: 4% · 2 ч · 260 BYN/сут / Эффект: +22 120 BYN за 14 дней / ЭФФЕКТИВНО» — числа ТОЛЬКО из SimulationDTO.
  4) «А если бы не сработало?» → branch=neg → NegativeBranch: брак 11%, потери 2 170; подпись «Компенсатор: износ узла ламинации (91→96%). Рекомендация: внеплановое ТО»; кнопка «Оформить ТО» (type=repair).
  5) NotificationLog (/journal): GET /api/notifications со статусами sent/skipped_no_token/failed.
  6) /decision/:id — решение+notification+BeforeAfter; базовый мобильный вид.
  7) build зелёный; grep пуст.
  НЕ ДЕЛАТЬ: backend; живая PDF-кнопка (задача C2).
  КОММИТ: feat(ui): decision loop + journal + before/after (stage 6)

### ЭТАП 7 — AI/PDF UI + кэш (08.11)
- [ ] **C2 · ReportPage, AiNote(финал), предзаполнение ai_cache** (§11.4; T7.2–T7.4)
  ФАЙЛЫ: src/pages/ReportPage.tsx; src/components/ai/AiNote.tsx (финал); src/api/queries.ts (useAi, useReport); backend/scripts/prefill_cache.py; backend/data/ai_cache.json (сгенерировать И ЗАКОММИТИТЬ; проверить, что .gitignore его НЕ исключает).
  ПРИЁМКА:
  1) ReportPage: кнопка → window.open('/api/report/executive.pdf?scenario='+scenario, '_blank').
  2) AiNote на демо-сценах отвечает <2 c из кэша (source="cache"); при offline — fallback без блокировки UI.
  3) prefill_cache.py прогоняет 5 сцен: chain fin_margin(main), whatif ops=6, forecast peak, simulate main, simulate neg; каждый ответ прошёл validate(); /api/ai/health → cache_size ≥ 5.
  4) build зелёный; pytest зелёный (test_ai_guard не сломан).
  НЕ ДЕЛАТЬ: вызывать AI на площадке; менять промпт/схему ai.py.
  КОММИТ: feat(ai,ui): prefill cache + report page (stage 7)

  **GATE G3:** полный демо-трек §16.2 (10 шагов) руками ≤ 4:00 на чистом state; затем OFFLINE_MODE=true + выключенный Wi-Fi — трек проходит целиком.

### ЭТАП 8 — Полировка, питч, ФРИЗ (09.11)
- [ ] **D1 · demoScript, сброс, мобильный вид, serve.py, backup, слайды** (§14.9; T8.1–T8.6)
  ФАЙЛЫ: src/lib/demoScript.ts (10 шагов §16.2 с подсветками); src/store/demo.ts + Header (сброс: scenario=main, refetch всех query, LossCounter=0); DecisionPage (мобильный); backend/app/serve.py (uvicorn + StaticFiles ../frontend/dist html=True, порт 8000); pitch/{slides,coverage,script}.md; pitch/backup-demo-v2.mp4 (1080p, без звука, POP на 1840/22120/1240); docs/demo-checklist.md; архив .zip репо.
  ПРИЁМКА:
  1) demoScript ≤ 4:00 (цель 3:40).
  2) «Сброс демо» → чистый main-state; повторный трек без артефактов.
  3) `cd backend; uv run python -m app.serve` → фронт+API на :8000; телефон по LAN-IP открывает /decision/:id.
  4) OFFLINE_MODE=true, Wi-Fi off: трек проходит (DeepSeek=cache, telegram=skipped_no_token+журнал, PDF локальный).
  5) pitch/coverage.md: все 16 галочек §17.2 проставлены и соответствуют коду.
  6) Финальный DoD (§15.3): pytest зелёный; build зелёный; grep пуст; /api/health 200; DevTools Network в offline — ноль внешних запросов; PDF открывается в Adobe Reader.
  НЕ ДЕЛАТЬ: любые новые фичи после этой задачи. **CODE FREEZE.**
  КОММИТ: chore: demo polish + pitch + backup (stage 8, CODE FREEZE)

### ЭТАП 9 — v2 (дельта после лекций 11.11)
- [ ] **T9 Security** (§6 PLAN-V2: masking, rbac, sanitize, audit, ollama, тесты, RoleSwitcher, аудит-модалка)  
  ФАЙЛЫ: backend/app/security/{__init__,masking,rbac,sanitize,audit}.py; backend/app/integrations/ai_provider.py (правка); backend/tests/{test_masking,test_rbac,test_sanitize}.py; frontend/src/components/layout/RoleSwitcher.tsx; frontend/src/components/security/SecurityAuditModal.tsx.  
  ПРИЁМКА: test_masking/rbac/sanitize зелёные; Network чист; свитчер live.  
  НЕ ДЕЛАТЬ: T10–T14.

- [ ] **T10 Ребрендинг** (§3 PLAN-V2: dictionaries, display-имена, dims, сезонность-комментарий, norms)  
  ФАЙЛЫ: backend/app/core/dictionaries.py; backend/app/data/scenarios/{main,neg,peak}.json (правка display); backend/data/seasonality.json (комментарий).  
  ПРИЁМКА: тесты v1 зелёные; Kolbus/Layflat/picPac/22:52 на экране.  
  НЕ ДЕЛАТЬ: математику, id узлов.

- [ ] **T11 Gateway+Экосистема** (§7 PLAN-V2: ingest, mapping, эмулятор, bitrix-эмуляция, status, digest, вкладка UI)  
  ФАЙЛЫ: backend/app/api/gateway.py; backend/app/core/ingest.py; backend/app/integrations/bitrix.py; backend/app/data/emulator.py; frontend/src/pages/EcosystemPage.tsx.  
  ПРИЁМКА: test_gateway; burst→алерт offline; 8 коннекторов.  
  НЕ ДЕЛАТЬ: реальные вызовы 1С/Битрикс.

- [ ] **T12 Паспорт+Клиент360** (§9–10 PLAN-V2: фикстуры, endpoints, drawers)  
  ФАЙЛЫ: backend/app/data/passports.py; backend/app/api/orders.py; backend/app/api/clients.py; frontend/src/components/orders/OrderTimeline.tsx; frontend/src/components/clients/Client360Drawer.tsx.  
  ПРИЁМКА: test_passport/client360; таймлайн с отклонениями.  
  НЕ ДЕЛАТЬ: T13–T14.

- [ ] **T13 Прогноз+Поручения+Digest** (§11–12 PLAN-V2: горизонт, закупки, summary, digest-отправка)  
  ФАЙЛЫ: backend/app/api/forecast.py (правка); backend/app/api/decisions.py (правка); backend/app/api/export.py; frontend/src/components/forecast/ForecastHorizon.tsx; frontend/src/components/decision/ExecutionStrip.tsx.  
  ПРИЁМКА: test_forecast_v2/execution/digest.  
  НЕ ДЕЛАТЬ: T14.

- [ ] **T14 Питч+полировка** (§16 PLAN-V2: script/slides/coverage, backup-видео, UX-аудит §13, MCP-скелет §8 если время)  
  ФАЙЛЫ: pitch/{script,slides,coverage}.md; pitch/backup-demo-v2.mp4; docs/demo-checklist.md; backend/app/mcp_server.py (скелет).  
  ПРИЁМКА: демо ≤3:00 ×3 прогона; DoD v2 весь.  
  НЕ ДЕЛАТЬ: новые фичи после DoD.

  **GATE G5 (конец Этапа 9):** pytest ≥82 passed; build зелёный; демо ≤3:00; DoD v2 (§15 PLAN-V2) полностью.

### ЭТАП 10 — Демо-дни (12–13.11, кода нет)
- [ ] **E1 · Площадка:** раскатка на venue-железе; HDMI/USB-C адаптеры; решение по OFFLINE_MODE по факту сети; 3 репетиции на месте; флешки ×2 с backup-видео и .zip; ноут-дубль.
- [ ] **E2 · Защита:** питч по script.md (3:00); ответы на вопросы жюри: «данные синтетика?» → «калибровка по публичным профилям CEWE/Shutterfly + адаптер под реальные данные (§2.3)»; «одна ли математика?» → «одна модель и одна константа 131 BYN/ч; ползунок — калибровочная кривая из 3 точек, согласована тестом».

## 4. Гейты (контрольные точки)
| Гейт | После | Условие прохождения |
|---|---|---|
| G1 | A3 | pytest ≥60 passed; все эндпоинты §9.2 в /docs отвечают по правилу; PDF с кириллицей открывается; PROD-1234 создаётся |
| G2 | B3 | build зелёный; шаги 2–5, 9 трека кликабельны; grep хардкода пуст |
| G3 | C2 | трек ≤4:00 руками; трек проходит в OFFLINE_MODE без сети |
| G4 | D1 | DoD §15.3 полностью; CODE FREEZE |

## 5. LOG (агент заполняет после каждой задачи)
| Задача | Дата | pytest | npm build | Примечание |
|---|---|---|---|---|
| A1 | | | | |
| A2 | 07.11.2026 | 68 passed | N/A (на очереди) | decisions + sqlite + jira-мок + telegram; PROD-1234 создаётся. |
| A3 | 07.11.2026 | 80 passed | N/A (на очереди) | guard анти-галлюцинаций (кэш + validate), exec PDF с кириллицей, роутеры. Провайдер заменён Gemini→DeepSeek (klinch cloud), см. ADR-0003. Позже добавлен `GET /api/report/executive.pdf` (report/tables.py: фикс пустой таблицы решений) + `test_pdf.py` → 82 passed. |
| B1 | 08.11.2026 | 82 passed (из A3) | зелёный (tsc -b && vite build, 159 modules) | T4.1–T4.4 закрыты: api/{types,client,queries}.ts, store/{ui,demo}.ts, lib/format.ts, vite-proxy, QueryClientProvider (main.tsx); layout/{Section,Modal,Toast,DemoBadge}.tsx (4 состояния, esc/backdrop, очередь тостов; таймеры независимы после фикса зависимостей useEffect); routes.tsx (/, /journal, /report, /decision/:id, /devkit) + заглушки страниц; скелет Dashboard — 7 секций. Header/ThemeSwitcher из задачи темизации, react-router обоснован ADR 0004. grep 1840\|41200\|22120 и `any` — пусто. |
| B2 | | | | |
| B3 | | | | |
| C1 | | | | |
| C2 | | | | |
| D1 | | | | |

## 6. Коммиты и ветки
Conventional: `feat(api): …`, `feat(ui): …`, `chore: …`. После каждой задачи: `git add . && git commit -m "…" && git push origin main`. Красный тест — не коммитим (§13.6). Ветки по желанию: feat/api, feat/ui-shell, feat/ui-charts, feat/ui-decision, feat/ai-report, feat/pitch (§13.4).

## 7. Фолбэки-шпаргалка (§16.1)
| Риск | Действие |
|---|---|
| Нет интернета | OFFLINE_MODE=true; DeepSeek из кэша; Telegram → журнал отправок |
| DeepSeek таймаут/брак | timeout 5 → validate → fallback-шаблон |
| Telegram токен пуст | status=skipped_no_token + NotificationLog + скринкаст |
| Демо упало | backup-demo-v2.mp4 (2 флешки) + .zip репо |
| Чужие цифры в AI | test_ai_guard + предзаполненный кэш |