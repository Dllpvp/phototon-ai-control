# AGENTS.md — Правила для AI-агентов (OpenCode / Klinch)

Этот проект — хакатонное демо-приложение «Фотопринт·Контроль» (управленческий MVP для фабрики фотокниг). 
Единственный источник правды по архитектуре и математике — файл `Readme.md` в корне проекта. Перед любой задачей сверяйся с ним (особенно §7 «математика», §8 «сценарии», §9 «API», §10 «UI»).

## 🛑 АБСОЛЮТНЫЕ ЗАПРЕТЫ (Читать в первую очередь)
1. **НИКАКОГО ХАРДКОДА В REACT.** Все экономические числа (1840, 41200, 22120, 131 и т.д.) живут ТОЛЬКО в `backend/app/core/anchors.py` и `constants.py`. Фронтенд только отрисовывает то, что пришло по API. Если тебе нужно число на экране — сначала добавь его в ANCHORS, напиши тест, и только потом выводи через API.
2. **НЕ МЕНЯЙ МАТЕМАТИКУ БЕЗ ТЕСТОВ.** Любое изменение в `backend/app/core/` (особенно `impact.py`, `simulate.py`, `anchors.py`) должно сопровождаться запуском `uv run pytest -q`. Если тесты красные — код не принимается.
3. **НЕ ДОБАВЛЯЙ ЗАВИСИМОСТИ СЛЕПО.** Новые пакеты (Python или npm) добавляются только если они критичны для демо, и это должно быть обосновано.
4. **РУССКИЙ ЯЗЫК В UI.** Весь интерфейс, тексты ошибок, названия метрик — на русском языке. Код (переменные, функции) — на английском. Валюта — BYN. Даты — в формате `ru-RU`.
5. **НИКАКИХ TODO В КОДЕ.** Если что-то не доделано — создай задачу, но не оставляй `TODO` в файлах без ссылки на неё.
6.  **Не выполняй более 8-10 вызовов инструментов подряд без ответа пользователю.** После каждого важного действия (создание/правка файла) давай краткий статус выполнения. Это нужно для работы в OpenCode.
7. **ПЛАН-V2.md — дельта. Readme.md (v1) — база. При конфликте побеждает PLAN-V2.**
8. **Якоря v1 неприкосновенны. Новое число на экране → ANCHORS_V2/CONSTANTS_V2 + тест.**
9. **id узлов v1 не переименовывать. Ребрендинг = только display-имена и dims.**
10. **Ни одного сырого ФИО/клиента/суммы во внешний LLM: только через security/masking.**
11. **Демо работает без сети: эмуляторы локальные, помечены бейджем «эмулятор».**
12. **Роли — демо-механика (заголовок X-Demo-Role), не строить настоящий auth.**
13. **Новые зависимости (mcp) — только через ADR.**
14. **Файл ≤ 300 строк. DTO — только в schemas.py. Фронт — без цифр и формул.**
15. **Каждый новый эндпоинт: DTO → core/сервис → роутер → тест → хук фронта.**
16. **Питч 3:00. Демо-прогон с таймером после каждого этапа.**
17. **Фолбэки: OFFLINE_MODE=true, кэш, эмуляторы, MCP не нужен для демо.**
18. **Не строить клиенты Треков 2 и 3 — только порты и заглушки-потребители.**
19. **Не хардкодить числа во фронте; не логировать сырые payload; не передавать сырой текст тикетов в LLM.**
20. **PLAN-V2 > Readme при конфликте доков.**
## 🏗 Архитектура и поток данных
Строгая однонаправленная архитектура. Не перепрыгивай слои:
`backend/data/*.json` + `backend/app/data/scenarios/*.json` ➔ `backend/app/core/` (чистая математика, без FastAPI) ➔ `backend/app/dependencies.py` и `backend/app/api/` (тонкие роутеры, DTO in/out) ➔ `frontend/` (только отрисовка).

Каталог данных можно переопределить переменной окружения `FOTOPRINT_DATA_DIR` (см. `backend/app/core/loader.py`).

- **Backend:** Python 3.12+ (пин в `backend/pyproject.toml`, обоснование — `docs/adr/0001-python-version.md`), FastAPI, Pydantic v2 (+ pydantic-settings), uvicorn. Точные версии зависимостей — только в `backend/pyproject.toml` / `uv.lock`; не дублируй их здесь.
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Recharts, Zustand, TanStack Query, framer-motion, lottie-web. Точные версии — только в `frontend/package.json`.
- **Интеграции (ПЛАН, ещё не реализованы):** Telegram (httpx, только исходящие), DeepSeek flash через klinch cloud (OpenAI SDK, temperature=0, JSON response_format, кэш + фолбэк), PDF (reportlab). Каталоги `app/integrations/`, `app/report/` пока пустые; SQLite-журнал (`app/db.py`) тоже ещё не написан.

## 📌 Текущее состояние (проверено в репозитории)
- **Ядро** (`backend/app/core/`) реализовано: `graph`, `loader` (JSON ➔ Pydantic, кэш `lru_cache`), `anchors`, `constants`, `interpolation`, `economics`, `impact`, `forecast`, `simulate`. `uv run pytest -q` ➔ всё зелёное (49 тестов).
- **API:** пока единственный маршрут `GET /api/health` (`app/main.py`). Роутеры в `app/api/` ещё не написаны.
- **Пустые файлы-заглушки (0 байт), их предстоит наполнить:** `app/schemas.py`, `app/config.py`, `app/db.py`, `app/serve.py`, `app/api/__init__.py`, `tests/conftest.py`, `docs/adr/0001-python-version.md`, `pitch/*.md`, `tasks.ps1`, `.env.example`.
- **Frontend:** стандартный Vite-стартер (`src/App.tsx` — демо-шаблон Vite), UI приложения ещё не начат.
- **Данные:** `backend/data/{graph,norms,seasonality,facts}.json` и `backend/app/data/scenarios/{main,neg,peak}.json` **отслеживаются git'ом**. Файлы в `backend/data/` пересоздаются командой seed (см. ниже) — не правь их руками.
- `jakub-skills/` — посторонний клон в `.gitignore`, к проекту не относится.

Очередь задач — PLAN.md: бери первую задачу с [x→] т.е. первую незакрытую [ ], выполняй цикл из §0 PLAN.md.
## 📝 Дисциплина задачи (Как агенту получать задания)
Каждая задача должна выполняться в формате:
- **ЦЕЛЬ:** (что делаем)
- **ФАЙЛЫ:** (какие файлы создавать/менять. НЕ трогай другие!)
- **ПРИЁМКА:** (какой тест должен стать зеленым или что должно появиться на экране)
- **НЕ ДЕЛАТЬ:** (явные ограничения)

*Пример правильной работы:* Если тебе дали задачу "Сделать ползунок What-If", ты меняешь только `WhatIfSlider.tsx`, `api/queries.ts` и, возможно, `api/whatif.py`. Ты НЕ трогаешь `core/simulate.py`.

## 🎨 Темизация (4 темы × 2 режима) — обязательно
Источник правды: Readme §10.1.1–10.1.5 + frontend/src/styles/theme.css.
Контракт токенов фиксирован: --bg,--panel,--panel-2,--hair,--hair-strong,--text,--muted,
--alert,--alert-soft,--warn,--warn-soft,--ok,--ok-soft,--accent,--accent-2,--paper,--paper-ink,--shadow,
плюс --font-display,--font-mono,--font-serif,--radius,--shadow-strength.

ЖЁСТКИЕ ПРАВИЛА:
1. Любой цвет/радиус/тень/шрифт — ТОЛЬКО через var(--токен) или утилиты theme.css (.card,.tag,.memo,.slider,.zen-slider,.crop,.dotfield,.edge-live,.calm-stream,.osc,.live-dot,.breathe-dot).
   ЗАПРЕЩЕНЫ hex-классы Tailwind по памяти: text-red-400, bg-slate-900, bg-gray-900, border-blue-*,
   from-*/to-* градиенты, rounded-xl/2xl/3xl, shadow-lg/xl/2xl. Они ломают переключение тем = reject.
2. Запрет-лист ФОРМЫ тема-зависим (Readme 10.1.1–10.1.4): mission → острые углы/hairline/без мягких теней;
   swiss → radius 4px + жёсткая тень-отпечаток; investor → radius 10px + мягкие тени + воздух; zen → radius 20px + мягкие тени + природные тона.
   НЕ смешивать признаки двух тем в одном компоненте. Если компонент должен выглядеть по-разному в темах —
   различай через var(--radius)/var(--shadow-strength) или условный класс по useThemeStore().theme, НЕ через хардкод.
3. framer-motion / CSS-анимации читают цвет ИЗ ТОКЕНА (var(--alert) и т.п.), НИКОГДА из строкового пропса
   или захваченного в closure значения — иначе при смене темы анимация замрёт со старым цветом.
4. Шрифты — только @fontsource (офлайн-сейф), НЕ <link> Google Fonts. Цифры/деньги/ID — класс .mono
   (tabular-nums). Заголовки — .display. AiNote/служебка — .memo + .serif.
5. Перед коммитом фронта прогнать grep по запрет-листу п.1 по frontend/src — результат пуст.
   И отдельно: grep -rn "fonts.googleapis" frontend/index.html frontend/src — пусто.
6. Новый компонент обязан рендериться корректно во ВСЕХ 8 комбинациях (прогнать ThemeSwitcher вручную
   или snapshot-тест по матрице theme×mode). Компонент, красивый только в mission, = дефект.
## 🧪 Тестирование и Проверка
- **Backend:** `uv run pytest -q` **из папки `backend/`** (иначе не подхватится `pyproject.toml`; настройки: `pythonpath=["."]`, `testpaths=["tests"]`). Тесты в `backend/tests/`: `test_anchors.py` (цифры бьются), `test_graph.py` (граф ацикличен), `test_impact.py` (BFS `delta`), `test_interpolation.py`, `test_forecast.py`, `test_simulate.py` (эффект решений: main=effective/22120, neg=ineffective). После правок в `core/` прогонять их обязательно.
- **Frontend:** линтер — **oxlint** (`npm run lint`), НЕ eslint. Типы проверяет сборка: `npm run build` (`tsc -b && vite build`) — ошибок быть не должно. `tsconfig.json` — только project references (`tsconfig.app.json` + `tsconfig.node.json`).
- **Проверка хардкода:** перед коммитом фронтенда grep'ом проверь, нет ли в `src/` чисел `1840`, `41200`, `22120`. Их там быть не должно.

## 🚀 Команды для запуска и проверки (Windows PowerShell)
Из корня проекта (каждая команда — из своей папки, поэтому `;`-переход):

- **Backend** (папка `backend/`):
  - Установка зависимостей: `cd backend; uv sync`
  - Генерация данных: `cd backend; uv run python -m app.data.seed --out data`
  - Тесты: `cd backend; uv run pytest -q`
  - Запуск сервера: `cd backend; uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- **Frontend** (папка `frontend/`):
  - Установка зависимостей: `cd frontend; npm install`
  - Линт: `cd frontend; npm run lint`
  - Сборка (проверка типов): `cd frontend; npm run build`
  - Dev-сервер: `cd frontend; npm run dev`

## 🤖 Работа с контекстом
- Один файл = одна тема. Максимум 300 строк на файл. Если файл разрастается — разбивай его.
- Все Pydantic DTO должны находиться в одном месте: `backend/app/schemas.py` (пока пуст — заполнять здесь, не разбрасывать DTO по роутерам).
- Все TypeScript-типы (зеркала DTO) должны находиться в `frontend/src/api/types.ts` (ещё не создан).
- Никогда не используй `any` в TypeScript.
- Язык ответов и текстов коммитов — русский; имена в коде — английские.