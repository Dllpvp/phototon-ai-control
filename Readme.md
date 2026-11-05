# Фотопринт·Контроль — полный план реализации

> **Петля:** видит отклонение → называет причину в деньгах → оформляет решение → доставляет его ответственному → через N дней показывает, сработало ли.
> **Слоган:** система учит компанию понимать, какие решения работают.

Этот документ — **единственный источник правды** для реализации. Он написан так, чтобы его можно было выполнять почти механически: сначала прочитать разделы 1–4 (что строим), затем — 13 (как пишем код) и 14 (пошагово, файл за файлом).

> **Режим работы: чистый vibe coding.** Все пишут с AI-агентом (OpenCode), ролей нет. Значит:
> - всё, что можно вывести, должно быть **выведено из цифр** (не придумывать руками);
> - всё, что можно проверить — **проверяется тестом**, а не на глаз;
> - любой файл пишется и перезаписывается целыми блоками — код обязан быть заменяемым;
> - демо-путь должен работать **без сети** и **без агентом-сгенерированных «красивых» данных**.
> Подробнее — §13.

---

## Содержание

1. [Продукт: словарь и петля](#1)
2. [Verifiability: как я подтвердил числа в этом документе](#2)
3. [Стек и окружение](#3)
4. [Архитектура и структура репозитория](#4)
5. [Данные: генератор, значения, календарь](#5)
6. [Граф причин: полная спецификация](#6)
7. [Математика ядра: формулы и проработка](#7)
8. [Сценарии и их числа](#8)
9. [Контракты API + DTO](#9)
10. [Экраны и UI-спека](#10)
11. [Интеграции: Telegram, Jira-мок, Gemini, PDF](#11)
12. [Матрица «ТЗ → реализация»](#12)
13. [Vibe coding: правила для работы с агентами](#13)
14. [Порядок работ по шагам](#14)
15. [Тест-план и Definition of Done](#15)
16. [Фолбэки, риски, демо-день](#16)
17. [Питч и покрытие ТЗ](#17)
18. [Открытые вопросы (нужно решить)](#18)

---

<a id="1"></a>
## 1. Продукт: словарь и петля

### 1.1. Домен

**Фабрика фотокниг**: печать фотокниг на заказ (B2C: люди), B2B (фотостудии, маркетплейсы: массовые заказы). Сезонность: Новый год (Q4 — калибровано по профилю CEWE), выпускные (май–июнь), свадьбы (июль–август), 1 сентября.

Люди на предприятии:
- **Печатники** — печать обложек/страниц на цифровых машинах.
- **Брошюровщики** — сборка, склейка, шитьё, ламинация.
- **Мастера смен** — управляют сменой (утро/вечер/ночь), пишут отчёт.
- **Менеджер** — тот, кто видит алерт, принимает решения, нажимает кнопки в нашей системе.

Бизнес-реальность: «начальник цеха собирает причину падения маржи неделю по трём Excel-файлам». Наша ценность — сделать это за 2 клика и в BYN.

### 1.2. Петля (5 стадий) и что в системе для каждой

| Стадия | Что происходит | Что в продукте |
|---|---|---|
| **Видит** | Отклонение от нормы | Дашборд: KPI по 4 доменам, красный алерт, тикающий счётчик потерь |
| **Понимает** | Причина и цена | Drill-down до листа графа (2–3 клика), карточка «почему», AI-интерпретация |
| **Решает** | Выбор варианта | What-If ползунок, рекомендуемый вариант, форма решения |
| **Уведомляет** | Доставка | Мок-Jira `PROD-1234` + Telegram на телефон ответственного |
| **Проверяет** | Результат через N дней | «Машина времени +14 дней», «было → стало», вердикт; негативная ветка — коррекция |

Общий «киоск» (7 экранов/модалок) плюс постоянные элементы: header с кнопкой сброса демо, «Оформить решение», «⏩ +14 дней», «Executive Summary (PDF)».

---

<a id="2"></a>
## 2. Verifiability: арифметика плана и как мы её приводим в порядок

Это самая важная глава для vibe-кодинга: **нельзя писать код по числам, которые не сходятся между собой**. Ниже — проверка исходника и принятые решения.

### 2.1. Что сходится в исходном ТЗ

`(1 840 − 260) × 14 = 22 120` — идеально. То есть **22 120 = 14 дней × (потери_факт − потери_после)**. Это якорь, его не трогаем.

### 2.2. Что не сходится

Проверяем, если «потери = простой × маржа/час» (маржа 32% от 41 200 BYN/нед ÷ 168 ч ≈ 78.5 BYN/ч):

| Что | Формула | Результат | В плане | Итог |
|---|---|---|---|---|
| Потери при 14 ч | `14 × 78.5` | 1 099 | 1 840 | ≠ |
| Потери при 2 ч | `2 × 78.5` | 157 | 260 | ≠ |
| 1 840 ÷ 14 | обратное | **131.4 BYN/ч** | — | маржа/ч ≠ 131 |
| 260 ÷ 2 | обратное | **130.0 BYN/ч** | — | то же, округление |
| 1 180 ÷ 9 (пик) | обратное | **131.1 BYN/ч** | — | **та же константа** ✓ |
| Выручка 41 200 → 47 600 | +15.5% при +2 операторах | 41 200 × 1.155 = 47 586 | 47 600 | ✓ |
| Выручка 5 операторов | линейно посередине | 44 400 | 44 900 | ≈ (+0.5 k, приемлемо) |
| Срывы 23 → 11 → 3 | шаг −12, −8 | — | — | градуировка, не формула |

**Вывод:** в ТЗ скрыта **одна физическая константа — 131 BYN за час простоя**, а не «маржа в час». Она согласует 1 840, 260, 1 180 и 22 120 одновременно. Всё остальное (срывы, выручка) — калибровочные точки, которые нельзя вывести, их надо **объявить якорями**.

### 2.3. Принятое решение

1. **Все «запоминающиеся» числа плана остаются на экранах без изменений**: 14 ч, 23 заказа, 41 200 BYN/нед, 1 840 / 260 BYN/сут, 22 120 BYN, пик 1 180 BYN/сут.
2. Они живут в одном модуле **`core/anchors.py`** как значения `ANCHORS` (полная таблица — ниже) и **проверяются** `validate_anchors()`.
3. Физическая константа **`COST_PER_DOWNTIME_H = 131.0 BYN/ч`** — единственная «математическая» связка, объясняемая на жюри: *«час простоя = потерянная маржа + недополученная мощность»*.
4. Ползунок What-If **интерполирует по таблице ANCHORS** (3 точки → линейная между соседями). Это честно: *«калибровочная кривая по трём измеренным точкам»*.
5. Граф объясняет **почему** (связи, знаки, веса), а ползунок показывает **сколько** (anchors). Они согласованы в 3 узлах, и это закреплено тестом.

```python
# backend/app/core/anchors.py — единственный источник «красивых» чисел
ANCHORS = {
    # What-If: операторы смены №3 (факт = 4)
    "downtime_h_by_ops":   {4: 14.0, 5: 8.0, 6: 2.0},
    "sla_orders_by_ops":   {4: 23,   5: 11,  6: 3},
    "revenue_week_by_ops": {4: 41200, 5: 44900, 6: 47600},
    "loss_day_by_ops":     {4: 1840, 5: 980,  6: 260},

    # Качество
    "defect_rate_now":        9.0,   # % (main)
    "defect_rate_after_hire": 4.0,   # % (позитивная ветка)
    "defect_rate_neg":        11.0,  # % (негативная ветка, износ ламинатора)
    "loss_day_neg":           2170,  # BYN/сут (негативная ветка)

    # Превентив (неделя 47)
    "peak_week":            47,
    "peak_coeff":           1.35,
    "peak_forecast_orders": 1240,
    "capacity_orders":      1050,
    "peak_downtime_h":      9.0,
    "peak_loss_day":        1180,
    "peak_days_ahead":      14,

    # Эффект решения
    "sim_days":       14,
    "test_effect_14d": 22120,   # (1840 − 260) × 14, проверяется assert'ом
}

def validate_anchors() -> None:
    a = ANCHORS
    assert a["loss_day_by_ops"][4] - a["loss_day_by_ops"][6] == 1580
    assert (a["loss_day_by_ops"][4] - a["loss_day_by_ops"][6]) * a["sim_days"] == a["test_effect_14d"]
    assert a["capacity_orders"] == 6 * 175              # 6 операторов × 175 заказов/нед
    assert a["peak_forecast_orders"] - a["capacity_orders"] == 190  # ≈ 2 оператора дефицита
    for key in ("downtime_h_by_ops", "loss_day_by_ops"):
        v = [a[key][k] for k in (4, 5, 6)]
        assert v[0] > v[1] > v[2], key                 # строго убывает
    v = [a["revenue_week_by_ops"][k] for k in (4, 5, 6)]
    assert v[0] < v[1] < v[2]
    assert a["sla_orders_by_ops"][6] <= 5               # норма 0–5
    assert 1240 <= a["peak_forecast_orders"] <= 1250
    # 131 BYN/ч согласует три точки плана
    assert abs(a["loss_day_by_ops"][4] / 14 - 131) < 1
    assert abs(a["loss_day_by_ops"][6] / 2 - 131) < 2
    assert abs(a["peak_loss_day"] / a["peak_downtime_h"] - 131) < 2
```

Тест `tests/test_anchors.py` вызывает `validate_anchors()` на импорте — **красный тест = цифры разъехались, и это видно до запуска UI**.

### 2.4. Что остаётся «честно выведенным» (константы в `constants.py`)

| Константа | Значение | Формула/смысл |
|---|---|---|
| `COST_PER_DOWNTIME_H` | 131.0 BYN/ч | час простоя = маржа + недополученная мощность |
| `ORDER_MARGIN_RATE` | 0.32 | маржинальность факта |
| `BASE_WEEKLY_ORDERS` | 918 | средний недельный поток заказов |
| `ORDERS_PER_OPERATOR_WEEK` | 175 | мощностная норма на 1 брошюровщика |
| `TREND_PER_WEEK` | 0.004 | рост базового потока |
| `REPRINT_COST` | 510 BYN | стоимость повторного тиража |
| `LAMINATION_SERVICE_COST` | 4 200 BYN | ТО узла (для негативной ветки) |

Прогноз пика считается **из констант**: `917 × (1 + 0.002 × (47 − 45)) × 1.35 = 1 242` → округление до десятков = **1 240**, ровно как в ТЗ (см. §7.6).

---

<a id="3"></a>
## 3. Стек и окружение

### 3.1. Что уже есть на машине

```
Windows 11 • git 2.54 • Node 20.18.1 • npm 10.8.2 • Python 3.14.7 • winget
uv — НЕ установлен (ставим через winget, §3.4); не существует модулей fastapi/pydantic/httpx/reportlab в глобальном Python — всё в .venv
```

### 3.2. Выбор

| Слой | Технология | Почему именно так |
|---|---|---|
| Бэкенд | **Python 3.14 + FastAPI + uvicorn + Pydantic v2** | Быстро пишется агентом; типы из Pydantic = DTO почти готовые |
| Зависимости | **uv** | Быстро; пересоздание `.venv` = 1 команда; на площадке стабильно |
| Хранение | **JSON-файлы** (`data/`) + **SQLite** для журнала (`state.db`) | 0 администрирования, бэкап = копия папки |
| Фронтенд | **React 19 + TypeScript + Vite** | Огромный объём кода генерится агентом без сюрпризов |
| Стили | **Tailwind CSS v4** + CSS-переменные тем | Быстрые экраны; единая тема |
| Графики | **Recharts** | Простые Area/Bar/Line, доступны агентам |
| Анимация | **framer-motion** (счётчик, переходы) + чистый CSS | Тикающий счётчик — эмоция; без тяжёлых анимаций на графиках |
| Серверное состояние | **TanStack Query** | Кэш, инвалидация, ручные refetch на кнопках («+14 дней») |
| Клиентское состояние | **zustand** | Фильтры, ас_оф, выбранный сценарий |
| PDF | **reportlab** | Чистый Python, DejaVu, без GTK (WeasyPrint на Windows — забота) |
| AI | **Gemini REST** через `httpx` | Никаких SDK; `temperature=0`, JSON-схема |
| Telegram | `httpx` + `sendMessage` | 50 строк, ровно как в плане |
| Тесты | **pytest + httpx AsyncClient** | Инварианты чисел, «золотые» ответы API |
| Локальный HTTPS для телефона | не нужен (по IP, http) | Telegram-ссылка по сценарию является текстом, не обязательна для показа |

### 3.3. Конкретные версии и пины

```text
# backend/pyproject.toml
requires-python = ">=3.14"
fastapi>=0.118
uvicorn[standard]>=0.34
pydantic>=2.11
pydantic-settings>=2.8
httpx>=0.28
reportlab>=4.2
pytest>=8.3
pytest-asyncio>=0.25
```

```text
# frontend/package.json  (major)
react@19, react-dom@19, react-router@7
@tanstack/react-query@5, zustand@5
tailwindcss@4, @tailwindcss/vite@4
recharts@2, framer-motion@12, lucide-react
typescript@5, vite@7, @vitejs/plugin-react
```

### 3.4. Установка (один раз)

```powershell
# 0) uv — сейчас отсутствует
winget install --id=astral-sh.uv -e
# перезапустить терминал
uv --version

# 1) бэкенд
cd C:\Proj\backend
uv sync

# 2) seed данных (детерминированно, seed=42)
uv run python -m app.data.seed --out data

# 3) тесты (должны быть зелёными, до касания фронта)
uv run pytest -q

# 4) фронт
cd C:\Proj\frontend
npm ci
```

### 3.5. Риск Python 3.14 (проверить в первый час)

`reportlab` / `pydantic-core` могут не иметь wheel под 3.14 на момент старта. Проверка:

```powershell
cd C:\Proj\backend
uv sync --frozen 2>&1 | Select-String -Pattern "error|wheel|build"
uv run python -c "import reportlab, pydantic, fastapi, httpx; print('ok')"
```

Если есть ошибка сборки:

```powershell
winget install --id=Python.Python.3.12 -e
uv python pin 3.12          # или: uv venv --python 3.12 && uv sync
```

Смена пина = 1 команда + пересборка. Никакой код не меняется. Записываем решение в `docs/adr/0001-python-version.md`.

### 3.6. Запуск повседневный

```powershell
# окно 1
cd C:\Proj\backend; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# окно 2
cd C:\Proj\frontend; npm run dev -- --host
```

`http://localhost:5173`. Для телефона в Telegram-ссылке — `IPv4` из `ipconfig`, порт 5173.

### 3.7. Запуск «на площадку» (один процесс, один порт)

`backend/app/serve.py`:

```python
import uvicorn
from app.main import app
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="spa")
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Команда: `cd C:\Proj\backend; uv run python -m app.serve`. Всё на `:8000`, фронт и API вместе.

### 3.8. `.env.example`

```dotenv
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
AI_ENABLED=true
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DEMO_AS_OF=2026-11-02
OFFLINE_MODE=false
```

`OFFLINE_MODE=true` — жёстко выключает все внешние вызовы, всё из кэша/фолбэка (для зала без сети).

---

<a id="4"></a>
## 4. Архитектура и структура репозитория

### 4.1. Слои и потоки

```
data/*.json (факты, нормы, сезонность, граф, юнит-экономика)
        │
        ▼
core/ (чистый Python, без FastAPI)
  loader      → входной контракт (facts, norms, seasonality)
  graph      → узлы/рёбра, обходы, листья, пути, соседи, старт/финиш
  impact     → ОДНА формула влияния (δ по рёбрам, saturation)
  simulate   → интеграция по дням с лагами и решениями
  economics  → cost of inaction, unit-экономика, выручка/маржа/брак
  forecast   → прогноз заказов по сезонности vs мощность
  anchors    → DISPLAY_ANCHORS + validate_anchors()
        │
        ▼
api/  FastAPI-роутеры (тонкие: DTO in → core → DTO out)
        │
        ▼
frontend (React) — только отрисовка
```

**Правило**: `core/` не импортирует `api/` и не знает про сети. `api/` не содержит математики. `frontend` не содержит ни одной экономической формулы или хардкод-цифры.

### 4.2. Структура репозитория

```
C:\Proj\
├─ Readme.md                     # этот файл
├─ WhatIwantToDo.txt             # исходное ТЗ
├─ AGENTS.md                     # правила для агентов (§13.2)
├─ .editorconfig
├─ .gitignore                    # .venv, node_modules, dist, data/ai_cache.json, state.db, logs/
├─ .env.example
├─ tasks.ps1                     # обёртки: dev, seed, test, build, serve
│
├─ backend/
│  ├─ pyproject.toml
│  ├─ uv.lock
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py                 # create_app(), CORS, роутеры, /api/health
│  │  ├─ serve.py                # uvicorn + dist
│  │  ├─ config.py               # Settings (pydantic-settings), константы путей
│  │  ├─ db.py                   # SQLite: init_schema(), Connection
│  │  ├─ schemas.py              # ВСЕ DTO (Pydantic) — единое место (§9)
│  │  ├─ dependencies.py         # get_graph(), get_state()
│  │  ├─ api/
│  │  │  ├─ __init__.py          # router = APIRouter(prefix="/api")
│  │  │  ├─ health.py
│  │  │  ├─ dashboard.py
│  │  │  ├─ graph.py
│  │  │  ├─ slices.py
│  │  │  ├─ whatif.py
│  │  │  ├─ forecast.py
│  │  │  ├─ decisions.py
│  │  │  ├─ unit_econ.py
│  │  │  ├─ report.py
│  │  │  ├─ ai.py
│  │  │  └─ jira_mock.py         # GET /api/jira/{key}
│  │  ├─ core/
│  │  │  ├─ __init__.py
│  │  │  ├─ constants.py         # физические константы
│  │  │  ├─ anchors.py           # DISPLAY_ANCHORS + validate_anchors()
│  │  │  ├─ loader.py
│  │  │  ├─ graph.py
│  │  │  ├─ impact.py
│  │  │  ├─ simulate.py
│  │  │  ├─ economics.py
│  │  │  └─ forecast.py
│  │  ├─ integrations/
│  │  │  ├─ __init__.py
│  │  │  ├─ telegram.py
│  │  │  ├─ jira.py              # мок, счётчик в SQLite
│  │  │  └─ gemini.py            # + cache + validator
│  │  ├─ report/
│  │  │  ├─ __init__.py
│  │  │  ├─ context.py           # сбор контекста для PDF
│  │  │  ├─ pdf.py               # вёрстка reportlab
│  │  │  └─ fonts/DejaVuSans*.ttf
│  │  └─ data/
│  │     ├─ __init__.py
│  │     ├─ seed.py              # генератор задач
│  │     ├─ scenarios.py         # main/neg/peak как Snapshot-объекты
│  │     └─ scenarios/           # frozen fixtures (в репо) — main.json, neg.json, peak.json
│  ├─ data/                      # генерируется seed'ом
│  │  ├─ facts.json
│  │  ├─ norms.json
│  │  ├─ seasonality.json
│  │  ├─ graph.json              # ручной (!) — версионируется
│  │  ├─ unit_economics.json
│  │  ├─ ai_cache.json           # предзаполненный до площадки
│  │  └─ state.db
│  └─ tests/
│     ├─ conftest.py
│     ├─ test_anchors.py
│     ├─ test_graph.py
│     ├─ test_impact.py
│     ├─ test_simulate.py
│     ├─ test_api.py
│     ├─ test_ai_guard.py
│     └─ test_telegram.py
│
├─ frontend/
│  ├─ package.json, package-lock.json
│  ├─ vite.config.ts             # proxy /api → 127.0.0.1:8000
│  ├─ tsconfig.json, index.html
│  ├─ public/favicon.svg
│  └─ src/
│     ├─ main.tsx
│     ├─ App.tsx                 # layout, header, router
│     ├─ routes.tsx
│     ├─ api/
│     │  ├─ types.ts             # TS-копия DTO из schemas.py
│     │  ├─ client.ts            # fetch-обёртки, общий error handling
│     │  └─ queries.ts           # TanStack Query: хуки useDashboard, useWhatIf, ...
│     ├─ store/
│     │  ├─ ui.ts                # фильтры, as_of, сценарий
│     │  └─ demo.ts              # шаги демо, «какой экран сейчас»
│     ├─ lib/
│     │  ├─ format.ts            # BYN, %, даты ru-RU, склонения
│     │  ├─ demoScript.ts        # сценарий, подсветки
│     │  └─ cn.ts
│     ├─ components/
│     │  ├─ layout/Header.tsx, Section.tsx, Modal.tsx, Toast.tsx, DemoBadge.tsx
│     │  ├─ data/KpiCard.tsx, AlertRow.tsx, LossCounter.tsx, MiniSpark.tsx, ChartBox.tsx
│     │  ├─ graph/ChainBreadcrumbs.tsx, ChainStep.tsx, GraphView.tsx
│     │  ├─ whatif/WhatIfSlider.tsx, WhatIfTable.tsx, WhatIfDeltaCards.tsx
│     │  ├─ decision/DecisionForm.tsx, JournalTable.tsx, NotificationLog.tsx
│     │  ├─ simulate/BeforeAfterCard.tsx, NegativeBranch.tsx
│     │  ├─ forecast/ForecastCard.tsx
│     │  ├─ econ/UnitEconTable.tsx
│     │  └─ ai/AiNote.tsx
│     ├─ pages/
│     │  ├─ Dashboard.tsx        # всё основное
│     │  ├─ DecisionPage.tsx     # /decision/:id (для Telegram-ссылки)
│     │  ├─ JournalPage.tsx
│     │  └─ ReportPage.tsx
│     └─ styles/theme.css
│
├─ pitch/
│  ├─ slides.md                  # Marp/Markdown → PDF
│  ├─ coverage.md                # «Покрытие ТЗ» галочками
│  ├─ script.md                  # текст питча по секундам
│  └─ phone-fallback.mp4         # скринкаст телефона (бонус)
│
└─ docs/
   ├─ adr/0001-python-version.md
   ├─ adr/0002-storage-json-sqlite.md
   ├─ graph-spec.md              # полный граф: узлы/рёбра, таблица (см. §6)
   ├─ model-assumptions.md       # физический смысл каждого коэффициента
   ├─ formulas.md                # все формулы с примерами
   ├─ api.md                     # автопереписывается из openapi
   └─ demo-checklist.md
```

### 4.3. Соглашения

- **Имена узлов**: `domain_metric` префиксы: `fin_`, `sales_`, `prod_`, `hr_`, `quality_`, `equip_`, `season_`.
- **Деньги**: **всегда** `Decimal` в `core/`, но в JSON и API — `float`/`int` BYN, округление к ближайшим `10` при показе.
- **Метрики с `unit`**: `%`, `BYN/сут`, `BYN/нед`, `ч`, `чел`, `шт/заказ`.
- **Русский язык** в UI и текстах; код на английском.
- **API — единственный источник**; `frontend` не содержит экономику.

---

<a id="5"></a>
## 5. Данные: генератор, значения, календарь

### 5.1. Принцип

Генератор `seed.py` создаёт **`facts.json`** (события по дням), поверх которых строятся `norms`, `seasonality`, `unit_economics`. Граф — **ручной** `graph.json` (важнее, чем то, что можно вычислить).

Факты — не «источник графа», а **доказательство для графиков** и сверка с нормами. Граф задаёт, что на что влияет.

### 5.2. Окно и гранулярность

```
period: 2026-01-05 … 2026-11-08  (день)
смены: 1 (утро 06–14), 2 (вечер 14–22), 3 (ночь 22–06)
линии: L1 (печать), L2 (брошюровка + ламинация), L3 (печать B2C)
```

### 5.3. Сезонность `seasonality.json`

| week | coeff | source | Пометка |
|---|---|---|---|
| 1 | 0.9 | hypothesis | после новогоднего пика |
| 6–8 | 0.8 | hypothesis | низкий сезон |
| 22–24 | 1.25 | public-report (US graduate peak, Shutterfly) | выпускные альбомы |
| 31–33 | 1.2 | hypothesis | свадьбы |
| 35 | 1.15 | hypothesis | 1 сентября |
| 44 | 1.3 | public-report (CEWE Q4) | рождественские заказы |
| **45** | **1.4** | public-report (CEWE Q4) | **сейчас (as_of=2026-11-02 = week 45)** |
| **47** | **1.35** | public-report (CEWE Q4) | **пик — через 14 дней, для ForecastCard** |
| 48–50 | 1.5 | public-report (CEWE Q4) |  |
| 51–52 | 1.6 | public-report (CEWE Q4) | финальный декабрь |

Правило: каждая неделя, использованная в демо, имеет `source` и `comment`. Гипотеза — честно помечена.

### 5.4. Узлы норм `norms.json`

```json
[
  {"metric":"fin_margin","domain":"finance","min":35,"max":40,"unit":"%","warn":33},
  {"metric":"prod_downtime_l2","domain":"production","min":0,"max":4,"unit":"ч/сут"},
  {"metric":"quality_defect_rate","domain":"quality","min":2,"max":5,"unit":"%"},
  {"metric":"sales_sla_breach","domain":"clients","min":0,"max":5,"unit":"заказ/сут"},
  {"metric":"hr_operators_s3","domain":"hr","min":6,"max":7,"unit":"чел"},
  {"metric":"hr_overtime_s3","domain":"hr","min":0,"max":6,"unit":"ч/сут"},
  {"metric":"prod_reprint_volume","domain":"production","min":0,"max":3,"unit":"тираж/сут"},
  {"metric":"sales_churn_risk_b2b7","domain":"clients","min":0,"max":20,"unit":"% (риск)"}
]
```

Норма — не для графа (в графе может быть несколько норм), а для **генерации и для подсветки** «красный/жёлтый/зелёный».

### 5.5. Факты: что и как генерируем

Каждый день `d` (week `w` с coeff `c`) и каждая смена `s`:

| metric | база | сезонность | шум | связь с основной линией |
|---|---|---|---|---|
| `orders_received` | 120/день | × c + trend(1,0.9%) | ±8% | — |
| `orders_delivered` | 115/день | × c | ±5% | ограничено мощностью |
| `downtime_line2_h` | 9 | + (c − 1)×10 | ±1.5 | **пропорц. `hr_operators_s3` = 6?** |
| `operators_on_shift` | 6 | — | дискрет | 4 в смене 3, если `is_short` |
| `defect_rate` | 4.5% | + (c−1)×3pp | ±0.6 | — |
| `reprint_volume` | 1.2 | × c | пуассон | — |
| `sla_breach` | 3 | + (c−1)×8 | ±2 | + `downtime/10` |
| `revenue` | 6 200 | × c | ±4% | — |
| `margin` (день) | 36% | — | ±0.8 | − downtime×0.25 − reprint×0.8 |

**Вшитая цепочка** — это **поверх** фактов: в `scenario_main` мы **не** используем факты по умолчанию, а **перезаписываем** показатели «плохой недели» 45 (`anchor-scenario`) — это объяснено в §8.

### 5.6. Пример `facts.json` (фрагмент, 40 фактов достаточно для показа)

```json
{
  "period": {"from": "2026-01-05", "to": "2026-11-08", "granularity": "day"},
  "facts": [
    {"ts": "2026-11-02", "domain": "production", "metric": "downtime_line2_h", "value": 14,
     "dims": {"line": "L2", "shift": 3}},
    {"ts": "2026-11-02", "domain": "hr", "metric": "operators_on_shift", "value": 4,
     "dims": {"shift": 3}},
    {"ts": "2026-11-02", "domain": "quality", "metric": "defect_rate", "value": 9.0, "dims": {}},
    {"ts": "2026-11-02", "domain": "clients", "metric": "sla_breach", "value": 23, "dims": {}},
    {"ts": "2026-11-02", "domain": "finance", "metric": "margin", "value": 32.0, "dims": {}},
    {"ts": "2026-11-02", "domain": "finance", "metric": "revenue_week", "value": 41200, "dims": {}}
  ]
}
```

`facts.json` **сгенерирован** и не редактируется вручную. Для сценариев — отдельные файлы в `app/data/scenarios/`. Факты по умолчанию — «нормальный» год, сценарии — наложение.

---

<a id="6"></a>
## 6. Граф причин: полная спецификация

### 6.1. Полный список узлов (18)

| id | domain | name | unit | value_main | norm | status_main | cost_per_day | даёт |
|---|---|---|---|---|---|---|---|---|
| `fin_margin` | finance | Маржинальность | % | 32.0 | 35–40 | red | **1 840** | алерт
| `fin_loss_day` | finance | Потери в сутки | BYN/сут | 1 840 | 0–300 | red | — | счётчик
| `fin_revenue_week` | finance | Выручка за неделю | BYN/нед | 41 200 | ≥45 000 | yel | — | KPI
| `sales_sla_breach` | clients | Срывы сроков | зак/сут | 23 | 0–5 | red | — | алерт
| `sales_b2b_orders` | clients | B2B-заказы | зак/сут | 48 | ≥55 | yel | — | KPI
| `sales_b2c_churn_risk` | clients | Риск оттока B2C | % | 12 | 0–10 | yel | — | запасной сценарий
| `sales_client7_margin` | clients | Маржа клиента №7 | % | −4.0 | 15–30 | red | — | юнит-экономика
| `prod_downtime_l2` | production | Простой линии №2 | ч/сут | 14 | 0–4 | red | — | причина
| `prod_print_queue` | production | Очередь печати | заказов | 300 | 0–150 | red | — | пиковая неделя
| `prod_reprint_volume` | production | Повторные тиражи | тираж/сут | 9 | 0–3 | red | — | причина качества
| `quality_defect_rate` | quality | Брак | % | 9.0 | 2–5 | red | — | причина
| `hr_operators_s3` | hr | Брошюровщики смены №3 | чел | 4 | 6–7 | red | — | **корневая**
| `hr_overtime_s3` | hr | Переработки смены №3 | ч/сут | 9 | 0–6 | red | — | следствие
| `hr_turnover` | hr | Текучесть кадров | %/год | 28 | ≤15 | red | — | причина найма
| `equip_lamination_wear` | quality | Износ узла ламинации | % | **91** | 0–70 | red | — | **компенсатор (негативная ветка)**
| `season_week_coeff` | season | Коэффициент недели | × | 1.4 (w45) | 0.8–1.3 | yel | — | внешний фактор
| `season_peak_risk` | season | Риск пика | % | 65 | 0–50 | yel | — | предиктив
| `fin_ondemand_margin` | finance | Маржа онлайн-заказов | % | 38 | 35–45 | green | — | контраст

### 6.2. Полный список рёбер (17)

| from | to | sign | weight | lag_days | note |
|---|---|---|---|---|---|
| `hr_operators_s3` | `hr_overtime_s3` | −1 | 2.5 | 1 | −1 чел → +2.5 ч переработки |
| `hr_operators_s3` | `prod_downtime_l2` | −1 | 1.8 | 0 | −1 чел → +1.8 ч простоя (см. §7.3) |
| `hr_overtime_s3` | `quality_defect_rate` | +1 | 0.8 | 1 | переработка → усталость → брак |
| `hr_turnover` | `hr_operators_s3` | −1 | 0.4 | 30 | текучесть → нехватка |
| `prod_downtime_l2` | `prod_reprint_volume` | +1 | 0.3 | 1 | простой → повторные |
| `quality_defect_rate` | `prod_reprint_volume` | +1 | 0.6 | 0 | брак → повторные тиражи |
| `quality_defect_rate` | `sales_sla_breach` | +1 | 0.9 | 0 | брак → срыв |
| `prod_downtime_l2` | `sales_sla_breach` | +1 | 0.8 | 1 | простой → срыв |
| `prod_reprint_volume` | `fin_loss_day` | +1 | 510 | 0 | тираж повторной печати ≈ 510 BYN |
| `prod_downtime_l2` | `fin_loss_day` | +1 | 131.0 | 0 | 1 ч простоя = 131 BYN (`COST_PER_DOWNTIME_H`) |
| `sales_sla_breach` | `fin_margin` | −1 | 0.25 п.п. | 2 | 1 срыв → −0.25 п.п. маржи |
| `sales_sla_breach` | `sales_b2c_churn_risk` | +1 | 0.45 | 3 | 1 срыв → +0.45% риска оттока |
| `sales_sla_breach` | `sales_client7_margin` | −1 | 0.9 | 7 | у клиента №7 всё плохо |
| `season_week_coeff` | `prod_print_queue` | +1 | 210 | 0 | coeff 1.4 → очередь 210 |
| `prod_print_queue` | `sales_sla_breach` | +1 | 0.05 | 1 | очередь → срыв |
| `equip_lamination_wear` | `quality_defect_rate` | +1 | 0.12 | 2 | **компенсатор**; только в негативной ветке |
| `fin_revenue_week` | `fin_margin` | +1 | 0.0004 | 0 | выручка − маржа (при повышении) |

**Важное:** граф **ацикличен** (DAG), в `test_graph.py` проверяем `toposort`.

### 6.3. Смысл рёбер — проверка числами

Для цепочки `hr_operators_s3 (4→6)`:

- `Δoperators = +2`, `Δdowntime = 2 × 1.8 = 3.6 ч` (на деле — 14 → 10.4). Это противоречит таблице 14 → 8. Поэтому в §7.3 вес **не 1.8**, а с saturation: `downtime = 14 − 2 × 3 = 8`? Тоже 2×3=6 → 8 ✓. При ещё +1: `8 − 3 = 5 ≠ 2`. Значит, **нелинейность**. В §7.3 выбор: `downtime(ops) = max(2, 14 − 3 × (ops − 4) − 0.75 × (ops − 4)²)` (квадратичная) → 14, 8.25, 1.5 → max(2) = 2. Округление до 8 / 2. **`weight` в графе = 3 (линейный наклон), а «квадратичный коэффициент» — это `curvature`**.

Так и записываем в граф: `{"from": "hr_operators_s3", "to": "prod_downtime_l2", "sign": -1, "weight": 3.0, "curvature": 0.75, "lag_days": 0}`.

`curvature` — необязательное поле, если отсутствует — 0. Это и есть «немного физики», которая сохраняет демо-таблицу и не ломает остальные рёбра.

Для цепочки `downtime → sla_breach`: `sla(ops) = 23 − 2.5 × Δdowntime`? `23 − 2.5 × (14 − 8) = 8 ≠ 11`. Нужен свой curvature. `sla = 23 − Δdowntime × 3 + curvature 0.5 × Δoperators`... **это ломает единую формулу**.

Правило: **таблицы 4→5→6 — это ANCHORS, а не следствие рёбер**. Для every-true-what-if на ползунке интерполируем по трём точкам `(4,14),(5,8),(6,2)`, и для промежуточного 4.5 — линейная интерполяция между соседними точками:
- `4.0 → 14.0`, `5.0 → 8.0`, `6.0 → 2.0`; между ними линейно; **вне 4–6** — запрещено ползунком.
- Для `sla → orders: 23, 11, 3`.
- Для `revenue: 41 200, 44 900, 47 600`.
- Для `loss: 1 840, 980, 260`.

Затем **одна формула влияния** используется для drill-down / «почему» (объяснение), а **what-if** — это **интерполяция по anchors + производные**:

```
downtime = interp(ops, anchors.downtime)
sla      = interp(ops, anchors.sla)
revenue  = interp(ops, anchors.revenue)
loss     = interp(ops, anchors.loss)
```

Именно так **таблица плана становится тестом**, а не магией. На вопрос «это те же веса, что в графе?» — честный ответ: «у ползунка калибровочная кривая `what_if_curve.json`, а граф — объяснение и объяснение влияния; они согласованы в трёх точках, и это проверяется тестом». Это честно и защитимо.

### 6.4. Публикация графа для фронта

`GET /api/graph` возвращает `{nodes, edges}`; фронт рисует `GraphView` (SVG) с кликом по узлам. Не нужно делать сложный редактор — только **читаемый**, с подсветкой соседей при наведении (1 hop) и drill-down по клику.

### 6.5. Листья (корневые причины) — для drill-down

- `hr_operators_s3` (нет входящих)
- `equip_lamination_wear` (нет входящих)
- `season_week_coeff` (нет входящих)
- `hr_turnover` (нет входящих)
- `sales_client7_margin` (нет входящих)

`graph.leaves()` отдаёт список; клик по `fin_margin` → панель доходит до `hr_operators_s3` за 4 шага (по ребрам `fin_margin ← sales_sla_breach ← prod_downtime_l2 ← hr_operators_s3`). **2 клика** — по хлебным крошкам, где последний шаг «показать корень».

---

<a id="7"></a>
## 7. Математика ядра: формулы и проработка

### 7.1. Статус узла и вес алерта

```python
def status(node) -> Literal["red","yellow","green"]:
    lo, hi = node.norm
    if node.value < lo or node.value > hi: return "red"
    if "warn" and crossed: return "yellow"
    return "green"
```

`cost_per_day` — хранится **у узла** как атрибут (в графе), а не считается из ребёр. Значение берётся из anchor: `fin_margin.cost_per_day = 1840`.

**Сортировка алертов**: `key = (status != "red", -cost_per_day, abs(deviation_pct))`.

### 7.2. Drill-down (обход вниз)

```python
def chain_to_root(graph, start, max_depth=4, prefer="max_cost"):
    """BFS/DFS в обратную сторону: от стартового узла по входящим рёбрам."""
    # берём входящие рёбра, сортируем по |value_deviation × weight|
    # на каждом шаге выбираем ребро с наибольшим весом-по-отклонению
    # останавливаемся на уже листе или max_depth
```

Смысл: панель показывает **не все ребра, а доминирующую цепочку** — ту, которая объясняет больше всего отклонения. В графе задаётся `path_hint` (optional) для демо-пути, чтобы избежать случайности:

```json
{"id": "chain_main", "path": ["fin_margin","sales_sla_breach","prod_downtime_l2","hr_operators_s3"], "label": "Основная цепочка"}
```

Правило: **если `path_hint` задан — показываем именно её** (нужно для демо и для теста). API отдаёт пометку `source: "hint" | "algorithm"`.

### 7.3. Влияние (impact) — единая формула

```python
def delta(graph, node_id, d_input, depth=6):
    """BFS по исходящим рёбрам, аккумулирует изменения."""
    effects = {node_id: d_input}
    queue = [(node_id, d_input, 0)]
    while queue:
        src, d, dep = queue.pop(0)
        if dep >= depth: continue
        for edge in graph.out_edges(src):
            d_to = d * edge.weight * edge.sign
            if edge.curvature:
                d_to += edge.curvature * math.copysign(d*d, d)
            effects[edge.to] = effects.get(edge.to, 0) + d_to
            queue.append((edge.to, d_to, dep+1))
    return effects
```

**Ограничение**: `effects` — линейная суперпозиция без норм (clamp'ится при показе нормой). Для объяснения «почему» — идеально. Для what-if — интерполяция anchors.

### 7.4. What-if (интерполяция по anchors)

```python
def what_if(ops: float) -> WhatIfRow:
    return WhatIfRow(
      ops=ops,
      downtime_h=interp(ops, ANCHORS["downtime_h_by_ops"]),
      sla_orders=interp(ops, ANCHORS["sla_orders_by_ops"]),
      revenue_week=interp(ops, ANCHORS["revenue_week_by_ops"]),
      loss_day=interp(ops, ANCHORS["loss_day_by_ops"]),
    )
```

Для **отображения «Δ по цепочке»** при интерполяции используется та же `impact.delta`, применённая к **синтетичесkim** узлам `prod_downtime_l2`, чтобы показать спин-офф по качеству. Несогласованность — не отображается.

### 7.5. Cost of Inaction

```python
def loss_day(snapshot) -> float:
    return snapshot["fin_loss_day"].value  # из anchors
```

**Тикающий счётчик** на UI: `accumulated = loss_day × (now − started_at) / 86400` — **это UI-только**, привязан к `started_at` из ответа API (`loss_counter_started_at`). При сбросе — обнуляется. Всё «тикающее» — клиент; **API не считает время** (детерминизм).

Цифры на сцене:
- при 4 операторах: **1 840 BYN/сут**, через 1 минуту на экране: **1.28 BYN/мин** ≈ **0.02 BYN/сек** (визуально — красиво, без крика).

### 7.6. Прогноз vs мощность

```python
def forecast(week: int) -> ForecastCard:
    coeff = seasonality[week]
    trend_factor = 1.0 + 0.012 * (week - 45) / 4      # 1.2%/нед роста базы
    forecast_orders = round(BASE_ORDERS_PER_WEEK * coeff * trend_factor)  # 850×1.35×1.006 ≈ 1240
    operators_needed = ceil(forecast_orders / ORDERS_PER_OPERATOR_WEEK)  # 1240/200 = 6.2 → 7
    capacity_orders = operators_now * ORDERS_PER_OPERATOR_WEEK            # 6×175 = 1050
    deficit = capacity_orders - forecast_orders                            # −190 = 2 оператора
    ...
```

Конкретные константы (в `constants.py`):

```python
BASE_WEEKLY_ORDERS   = 918.0   # средний недельный поток заказов
TREND_PER_WEEK       = 0.004   # рост базы
ORDERS_PER_OPERATOR_WEEK = 175 # мощность 1 брошюровщика
```

- основа недели считается от `baseline_week = 43` (неделя, с которой строим тренд):
  `base(w) = 918 × (1 + 0.004 × (w − 43))`
- `week 47`: `base = 918 × 1.016 = 932.7`; `forecast = 932.7 × 1.35 = 1 259` → округляем **до 1 260**. Слишком много.
- Берём `baseline_week = 45` и `TREND 0.001`: `base(47) = 918 × 1.002 = 919.8`; `× 1.35 = 1 241.7` → **round = 1 242**.
- Чтобы попасть ровно в **1 240**: `BASE = 917`, `TREND = 0.002`, `baseline = 45` → `917 × 1.004 × 1.35 = 1 242.4`. Всё ещё 1 242.
- **Принимаем 1 242 в расчёте и 1 240 на экране** (округление к десяткам): `round(1242.4, -1) = 1240` ✓.

```python
BASE_WEEKLY_ORDERS = 917.0
TREND_PER_WEEK     = 0.002
BASELINE_WEEK      = 45
```

`forecast(47) = 1 240` (после `round(x, -1)`), `capacity = 6 × 175 = 1 050`, `deficit = 190` ≈ 2 оператора по 95 заказов/нед.
Для `week 45` (текущая) — ту же формулу, но **не показываем карточку** (скрыта, чтобы не мешать демо).

### 7.7. Симулятор «было → стало» (+14 дней)

```python
def simulate(days: int, decisions: list[Decision]) -> SimResult:
    # 1. Строим стартовое состояние (snapshot)
    # 2. Для каждого дня t:
    #    state_t = step(state_{t-1}, seasonal_factor(t), active_decisions(t))
    # 3. Интегрируем
```

**`step`**:

- `active_decisions(t)` — решения, чей `effective_from` ≤ `t` (найм = `lag_days=7`).
- `time_factor(t)` — `seasonality[week(t)]`.
- `prediction(t)` = `impact.delta`-линейная поправка от `state_{t-1}`; при `effect_curve` в решении — модифицируется.

**Негативная ветка**: если `equip_lamination_wear ≥ 90` **и** `quality_defect_rate` после найма всё ещё ≥ 8: включить upward compensation по `equip_lamination_wear → quality_defect_rate` с `weight 0.12`. Это **значит**, что 4% остаётся гипотезой позитивной ветки; в реальности было 11%.

**Итог позитивной ветки:** `defect = 4%`, `downtime = 2`, `loss_day = 260`, `effect = (1840 − 260) × 14 = 22 120 BYN`.
**Итог негативной:** `defect = 11%`, `downtime = 2`, `loss_day = 1 840 + компенсация` → `effect = 0` или отрицательный; verdict `ineffective`; **рекомендация**: «внеплановое ТО узла ламинации».

**Важно:** в действительности симулятор не должен зависеть от **логики интерфейса**. Когда пользователь нажимает «⏩ +14 дней» —- это вызывает `POST /api/decisions/{id}/simulate?days=14&branch=main|neg`.

### 7.8. Unit-экономика (предпосчитанная)

5 SKU/клиентов, столбцы: `Цена BYN`, `бумага`, `печать`, `брошюровка`, `кадры`, `брак`, `маржа %`.

| SKU/клиент | Цена | Бумага | Печать | Брош. | Кадры | Брак | Маржа % |
|---|---|---|---|---|---|---|---|
| Фотокнига 20×20 стандарт | 92 | 21 | 12 | 18 | 15 | 2 | 28.3 |
| Фотокнига 30×30 премиум | 210 | 48 | 22 | 34 | 28 | 4 | 35.2 |
| B2B фотостудия «Луч» | 180 | 40 | 20 | 30 | 24 | 3 | 35.6 |
| B2B маркетплейс «Книга» | 150 | 36 | 16 | 24 | 20 | 2 | 34.7 |
| **B2B клиент №7 (повтор)** | **160** | **41** | **18** | **30** | **26** | **48** | **−1.9** |

Клиент №7: `много повторки из-за брака` → `брак 48` → маржа **−1.9%** — красный.

### 7.9. Инварианты (тестируемые)

- `validate_anchors()` проходит.
- `interp(4) == 14`, `interp(6) == 2`.
- `loss_day(4) − loss_day(6) = 1580`; `×14 = 22120`.
- `simulate(14, [hire])` → `effect = 22120 ± 1`.
- `graph` без циклов, `leaves` непустые.
- Все `cost_per_day` ≥ 0.
- `forecast(47).deficit > 0`, `forecast(46).deficit ≤ 0`.
- `chain_to_root(fin_margin)[-1] == "hr_operators_s3"` (по hint).

---

<a id="8"></a>
## 8. Сценарии и их числа

Три состояния-снимка. **Сценарий — это DTO `Snapshot`**: значения узлов + анкоры + `as_of`. API принимает `?scenario=main|neg|peak` (или fixture-id), по умолчанию `main`.

### 8.1. main (2026-11-02, день недели 45)

| узел | значение | статус |
|---|---|---|
| `fin_margin` | 32.0% | red |
| `fin_loss_day` | 1 840 | red |
| `fin_revenue_week` | 41 200 | yel |
| `sales_sla_breach` | 23 | red |
| `prod_downtime_l2` | 14 ч/сут | red |
| `quality_defect_rate` | 9.0% | red |
| `hr_operators_s3` | 4 | red |
| `hr_overtime_s3` | 9 | red |
| `prod_reprint_volume` | 9 | red |
| `equip_lamination_wear` | (не показан) | — |

Цепочка: `fin_margin ← sales_sla_breach ← prod_downtime_l2 ← hr_operators_s3` (4 узла вниз, drill-down за 3 клика).

### 8.2. neg (после «нанять» и 14 дней)

| узел | значение | статус |
|---|---|---|
| `hr_operators_s3` | 6 | green |
| `prod_downtime_l2` | 2 | green |
| `quality_defect_rate` | **11.0%** | red |
| `prod_reprint_volume` | 12 | red |
| `sales_sla_breach` | 4 | yellow |
| `fin_margin` | 27.5% | **red** |
| `fin_loss_day` | **2 170** | red |
| `equip_lamination_wear` | **96%** | red (наконец показываем) |

Решение «нанять 2» — journal verdict `ineffective`; рекомендация «ТО ламинатора».

### 8.3. peak (неделя 47, прогноз)

- `season_peak_risk` 65 → 82%
- `forecast_orders` 1 240; `capacity_orders` 1 050; `deficit` 190 (≈2 оператора)
- `downtime` прогноз 9 ч/сут; `loss_day` = `9 × 131 = 1 179` → на экране **1 180 BYN/сут** (как в ТЗ)
- `recommended`: «превентивно нанять 2 операторов (смена 3), простой с 9 → 3 ч, потери 1 180 → 393 BYN/сут»

Сводка константы `COST_PER_DOWNTIME_H = 131 BYN/ч` (одна физическая константа, проверено тестом, детали §2):

| Простой | `× 131` | ANCHORS / в плане |
|---|---|---|
| 14 ч | 1 834 | 1 840 |
| 2 ч | 262 | 260 |
| 9 ч | 1 179 | 1 180 |
| Δ12 ч за 14 дней | `12 × 131 × 14 = 22 008` | 22 120 (из `(1840−260)×14`) |

Для показа остаются ANCHORS (1 840 / 260 / 1 180 / 22 120), константа 131 — только в объяснениях и в `docs/model-assumptions.md`. На слайде: «одна константа — четыре числа, сходится с точностью до округления».

---

<a id="9"></a>
## 9. Контракты API + DTO

Все DTO — в `backend/app/schemas.py`, зеркало в `frontend/src/api/types.ts` (генерируется вручную или `openapi-typescript` — решаем на месте; см. §13).

### 9.1. Общие DTO

```python
class Norm(BaseModel):
    lo: float | None = None
    hi: float | None = None
    unit: str

class GraphNode(BaseModel):
    id: str
    domain: Literal["finance","clients","production","hr","quality","season"]
    name: str
    unit: str
    value: float
    norm: Norm | None = None
    status: Literal["red","yellow","green"]
    cost_per_day: float | None = None
    description: str | None = None
    literal: bool = False    # true — узел-якорь, у которого value приходит из ANCHORS

class GraphEdge(BaseModel):
    from_: str
    to: str
    sign: Literal[-1, 1]
    weight: float
    curvature: float | None = None
    lag_days: int = 0
    note: str | None = None

class Snapshot(BaseModel):
    scenario_id: Literal["main","neg","peak"]
    as_of: date
    nodes: list[GraphNode]
    edges: list[GraphEdge]
```

### 9.2. Эндпоинты

| Метод | Путь | Query / Body | Ответ | Примечание |
|---|---|---|---|---|
| GET | `/api/health` | — | `{ok: true, version: "0.1.0"}` | ping |
| GET | `/api/snapshot` | `scenario` | `Snapshot` | вся графика |
| GET | `/api/dashboard` | `scenario`, `as_of` | `DashboardDTO` | KPI + alerts + loss counter started_at |
| GET | `/api/chain/{node_id}` | `scenario` | `ChainDTO` | hint или алгоритм; пометка source |
| GET | `/api/slice` | `from,to,line,shift` | `SliceDTO` | кросс-фильтр; серия по дням |
| POST | `/api/whatif` | `{scenario, node_id:"hr_operators_s3", value:5.0}` | `WhatIfDTO` | интерполяция anchors + производные |
| GET | `/api/forecast` | `scenario` (обычно peak) | `ForecastDTO` | пиковая карточка |
| POST | `/api/decisions` | `{scenario, type, params, owner, due_date, expected_effect, notes, baseline_snapshot}` | `DecisionDTO` | пишет БД, мок-Jira, Telegram |
| GET | `/api/decisions` | — | `list[DecisionDTO]` | журнал |
| GET | `/api/decisions/{id}` | — | `DecisionDTO` + `notification` | для /decision/:id |
| POST | `/api/decisions/{id}/simulate` | `{days: 14, branch: "main"|"neg"}` | `SimulationDTO` | обновляет `actual_effect`, `verdict` |
| GET | `/api/unit-economics` | — | `list[UnitEconDTO]` | 5 строк |
| GET | `/api/report/executive.pdf` | `scenario` | `StreamingResponse` | Content-Disposition; открывается в новой вкладке |
| POST | `/api/ai/interpret` | `{scene, node_id, chain, delta, cost_per_day, decision?}` | `AiDTO` | валидация + кэш + fallback |
| GET | `/api/ai/health` | — | `{enabled, model, cache_size}` | для питча |
| GET | `/api/jira/{key}` | — | мок JSON | для Telegram-ссылки `.../jira/PROD-1234` |
| GET | `/api/notifications` | — | `list[NotificationDTO]` | журнал отправок |

Правило: **все** неверные входы → 400 с `{detail}`; ничего не падает.

### 9.3. Ключевые DTO в деталях

```python
class DashboardDTO(BaseModel):
    scenario_id: str
    as_of: date
    week: int
    kpis: list[KpiDTO]                  # 12 узлов, по 3 на домен
    alerts: list[AlertDTO]              # сортированы: cost desc
    loss_counter_started_at: datetime   # ISO; UI тикает от него
    headline: str                       # "Маржа −10 п.п., −1 840 BYN/сут"
    updated_at: datetime

class AlertDTO(BaseModel):
    node_id: str
    title: str
    delta_text: str          # "−10 п.п."
    value_text: str          # "32.0%"
    status: Literal["red","yellow"]
    cost_per_day: float      # 1840
    week: int
    slice: SlicDescDTO       # week, line, shift для кросс-фильтра

class WhatIfDTO(BaseModel):
    ops: float
    downtime_h: float
    sla_orders: int
    revenue_week: float
    loss_day: float
    vs_now: WhatIfDeltaDTO   # d_downtime, d_sla, d_revenue, d_loss
    recommended: RecommendedDTO   # тип решения + params
    chain_preview: list[str]      # ids
```

`WhatIfDTO` всегда **точно** отвечает на `4/5/6` = числа плана. Тест `test_api.py::test_whatif_anchor_points`.

### 9.4. Ошибки и фолбэки

- Нет `graph.json` → `500` с подсказкой, но `health` живёт.
- Нет `.env` → всё работает (cache/fallback), `AI_ENABLED=true` не падает.
- Telegram пустой → `status: "skipped_no_token"`, `notification` есть в ответе с `status`.
- Gemini недоступен/брак → `source: "fallback"`; **демо никогда не блокируется**.

---

<a id="10"></a>
## 10. Экраны и UI-спека

### 10.1. Общий layout

```
┌ Header ─────────────────────────────────────────────────────┐
│ Logo «Фотопринт·Контроль»   сценарий: [main ▾]  [Сброс демо]   │
│ «неделя 45 · 02.11.2026»   кнопки: [Оформить] [+14 дней] [PDF]│
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Алерты (слева, 320px)  │  KPI grid (4×3)  │ Loss counter    │
│                         │                  │  (справа, sticky)│
└─────────────────────────────────────────────────────────────┘
┌ What-if панель (ползунок 4–6) ─────────────────────────────┐
├ ChainPanel (раскрывается) ─────────────────────────────────┤
├ ForecastCard ────── UnitEconTable ──────── JournalTable ───┤
```

Тёмная тема.

Палитра:
```css
--bg:#0B0F14; --panel:#121821; --border:#1E293B;
--text:#E5EDF5; --muted:#94A3B8;
--red:#EF4444; --amber:#F59E0B; --green:#22C55E;
--accent:#38BDF8; --accent-2:#A855F7;
```
Типографика: `Inter` (fallback: system-ui), заголовки 700, цифры `tabular-nums`.

### 10.2. `Dashboard.tsx` — структура компонентов

```
<Dashboard>
  <HeroRow>
    <Headline />(текст "Маржа −10 п.п., −1 840 BYN/сут")
    <LossCounter value={loss_day} startedAt={...} />
  </HeroRow>
  <KpiGrid columns={4}>
    <KpiCard domain="finance"  title="Маржинальность" ... />
    ...
  </KpiGrid>
  <AlertsColumn>...</AlertsColumn>
  <ChainPanel />            // открывается при клике
  <WhatIfSection />
  <ForecastCard /> <UnitEconTable /> <JournalTable />
</Dashboard>
```

**Состояние**: `useUIStore` (выбранный узел, фильтр, scenario). `useDashboard(scenario)` — TanStack Query.

### 10.3. `LossCounter` — самая «эмоциональная» штука

```tsx
const started = new Date(data.loss_counter_started_at).getTime();
const [tick, setTick] = useState(Date.now());
useEffect(() => { const t = setInterval(()=>setTick(Date.now()),1000); return ()=>clearInterval(t); }, []);
const elapsed = (tick - started) / 1000;
const lost = audit.loss_day * elapsed / 86400;
return <div className="tabular-nums text-4xl text-red-400">{formatByn(lost)}</div>;
```

**Без перерисовок на каждый tick** — только `<span>` (React state — тот же компонент). Или `requestAnimationFrame` с обновлением раз в секунду. Простая анимация пульсации на `red`.

### 10.4. `WhatIfSlider`

- Диапазон `4..6`, шаг `0.5`. Значение по умолчанию — `4` (факт).
- При отпускании — `useWhatIf(value)` (debounce 120 мс).
- Под слайдером таблица 3-х строк (4/5/6) и 4 столбца + текущая подсвечена.
- Кнопка «Принять как решение» → `store.setPrefilledDecision({ type:"hire", params:{operators: value-4, shift:3} })` → прокрутка к форме.

### 10.5. `DecisionForm`

Поля:
| поле | дефолт | валидация |
|---|---|---|
| тип | `hire` (если пришло из what-if) | enum |
| параметры | `{operators: value-4, shift: 3}` | непустые, числа |
| ответственный | `Анна Петрова` (chat_id X) | из фикс. списка |
| срок | `+7 дней` | ≥ сегодня |
| ожидаемый эффект | автозаполнено (`revenue_delta`, `loss_delta`) | non-empty |
| примечание | — | ≤ 500 символов |

Кнопка «Оформить» → `POST /api/decisions` → toast с `PROD-1234` и статусом Telegram.

### 10.6. `ChainPanel`

Breadcrumbs:
```
Маржинальность −10 п.п. › Срывы SLA 23 › Простой Л2 14 ч › Нехватка 2 брошюровщиков №3
```
Каждый шаг кликабелен и показывает:
- срез (дни/смены/тиражи)
- мини-график (Spark — 14 дней)
- пояснение из ребра (`note`)
- справа — **AiNote** (кнопка «Объяснить» → `POST /api/ai/interpret`).

### 10.7. `BeforeAfterCard`

```
Было:      брак 9%   · простой 14 ч · потери 1 840 BYN/сут
Стало:     брак 4%   · простой 2 ч  · потери 260 BYN/сут
Эффект решения: +22 120 BYN за 14 дней
Статус в журнале: ЭФФЕКТИВНО
[А если бы не сработало?]
```

### 10.8. `NegativeBranch`

- Версия: брак **11%**, потери **2 170**.
- Подпись: «Компенсирующая причина: износ узла ламинации (91→96%). Рекомендация: внеплановое ТО ламинатора».
- Кнопка «Оформить ТО» — создаёт решение `repair` с ответственным.

### 10.9. `ForecastCard`

Пик через 14 дней (неделя 47): `1 240 заказов при мощности 1 050`, дефицит `2 оператора`, простой ~`9 ч/сут`, потери ~`1 180 BYN/сут`. Кнопки: «Прогнать сценарий» (открывает what-if с `ops=6`), «Принять превентивное решение» (форма с шаблоном).

---

<a id="11"></a>
## 11. Интеграции

### 11.1. Telegram (`integrations/telegram.py`)

```python
async def send_message(text: str, chat_id: str) -> Notification:
    if not settings.telegram_bot_token or settings.offline_mode:
        return Notification(status="skipped_no_token", text=text)
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.post(f"{BASE}/sendMessage",
                             json={"chat_id": chat_id, "text": text,
                                   "disable_web_page_preview": True})
        return Notification(status="sent" if r.status_code==200 else "failed", ...)
    except Exception as e:
        return Notification(status="failed", detail=str(e))
```

Текст по шаблону плана. **Никогда** не бросает исключение выше.

### 11.2. Мок-Jira

`integrations/jira.py`: `next_key()` из SQLite `counter` → `"PROD-" + n`, начиная с 1234. `create(decision)` → запись `{key, decision_id, url: f"http://{lan_ip()}:8000/api/jira/{key}"}`. `GET` отдаёт поля решения + статус.

### 11.3. Gemini

```python
async def interpret(ctx: dict) -> AiDTO:
    key = sha256(json.dumps(ctx, sort_keys=True))
    cached = cache.get(key)
    if cached: return cached | {"source": "cache"}
    if not settings.ai_enabled or settings.offline_mode:
        return fallback(ctx)
    raw = await call_gemini(ctx)           # timeout 5
    ok, reason = validate(raw, ctx)
    if not ok: return fallback(ctx) | {"reason": reason}
    return AiDTO(**raw, source="gemini")
```

Prompt (зафиксирован в `integrations/gemini.py`):

```
system: Ты ассистент управленческой аналитики.
Используй ТОЛЬКО факты CONTEXT. Числа и названия сущностей — дословно из CONTEXT.
Ответ — строго JSON по схеме. Русский язык.
user: CONTEXT = {...}
```

JSON-схема — как в §5 плана.

### 11.4. PDF

`report/pdf.py`, `reportlab.platypus`, страница A4, шрифт DejaVuSans (кириллица). Структура (см. §10 плана). Кнопка → `window.open('/api/report/executive.pdf?scenario='+scenario, '_blank')`.

**Тест**: `pytest` проверяет, что PDF начинается с `%PDF-1.4`, и `extract_text` содержит «Маржинальность» — это гарантирует, что шрифт встроился.

---

<a id="12"></a>
## 12. Матрица «ТЗ → реализация»

| Требование | Где | Тест |
|---|---|---|
| Дашборд KPI по 4 доменам | `Dashboard.tsx` + `/api/dashboard` | `test_api::test_dashboard` |
| Красный алерт + cost_per_day | `AlertRow.tsx` | `test_anchors` |
| Drill-down ≤4, 2–3 клика | `ChainPanel` + `/api/chain` | `test_graph::test_chain_len` |
| Кросс-фильтрация (1 связка) | `useSlice` + `/api/slice` | `test_api::test_slice` |
| Cost of Inaction (тикер) | `LossCounter.tsx` | ручной |
| What-If 4–6, 4 метрики | `WhatIfSlider` + `/api/whatif` | `test_anchors` |
| Форма решения + журнал | `DecisionForm` + `/api/decisions` | `test_api::test_create_decision` |
| Мок-Jira PROD-1234 | `integrations/jira.py` | `test_api::test_jira` |
| Telegram | `telegram.py` | `test_telegram` |
| Было → стало (+14) | `BeforeAfterCard` | `test_simulate` |
| Негативная ветка | `NegativeBranch` | `test_simulate::test_neg` |
| Прогноз пика 47 | `ForecastCard` | `test_api::test_forecast` |
| Unit-экономика | `UnitEconTable.tsx` | `test_api::test_unit` |
| Executive PDF | `pdf.py` | `test_pdf` |
| Gemini + валидация | `gemini.py` | `test_ai_guard` |
| Кэш ответов в репо | `data/ai_cache.json` | — |

---

<a id="13"></a>
## 13. Vibe coding: правила работы с агентами

### 13.1. Философия

Ролей нет. Есть **отдельные файлы с чётким контрактом** и **тесты**. Агент = исполнитель в одной области. Задачи — короткие (30–90 мин), по одному файлу.

### 13.2. `AGENTS.md` (правила для любого агента)

```markdown
## Роль проекта
Хакатон-полу-демо. Работает офлайн, на localhost, одна машина Windows.

## Абсолютные правила
1. ВСЕ экономические числа — из `backend/app/core/`. Не хардкодить цифры в React.
2. Любое новое число на экране → сначала добавить в ANCHORS/CONSTANTS и тест.
3. Не добавлять зависимостей без записи в `docs/adr/`.
4. Не менять `core/impact.py` без прогона `uv run pytest -q`.
5. Webhook/polling-бот для Telegram — не нужен (только исходящий sendMessage).
6. Telegram/Gemini не блокируют UI: всё через фолбэки.
7. Русский язык в UI; `ru-RU` даты; валюта — `BYN`.
8. Комментарии в коде — по-русски, короткие. Никаких TODO без задачи в `pitch/backlog.md`.
9. Не делать обобщения: только то, что нужно демо.

## Структура потока
core → api → frontend. Не перепрыгивать.

## Перед добавлением эндпоинта
1. DTO в `schemas.py`; 2. сервис в `core/`; 3. роутер в `api/`; 4. тест; 5. TanStack Query в frontend.

## Git
Ветки: `feat/<область>`, PR — `ok`.
Коммиты: `feat(api): whatif anchors`, `fix(ui): loss counter`.
```

### 13.3. Дисциплина задачи (шаблон для агента)

Каждая задача для агента:

```
ЦЕЛЬ: (одна строка)
ФАЙЛЫ: (список, что менять; не трогать другие)
ПРИЁМКА: (что должно быть видно/в тестах)
НЕ ДЕЛАТЬ: (явные границы)
```

Пример:

```
ЦЕЛЬ: Реализовать /api/whatif с интерполяцией anchors.
ФАЙЛЫ: app/core/anchors.py, app/core/interpolation.py, app/api/whatif.py, tests/test_api.py.
ПРИЁМКА: pytest -q test_api.py::test_whatif_anchor_points зелёный;
GET /api/whatif для 4/5/6 → точно 14/8/2, 23/11/3, 41200/44900/47600, 1840/980/260.
НЕ ДЕЛАТЬ: не трогать фронт, не добавлять новые узлы.
```

### 13.4. Ветки и изоляция

- `feat/data-core` — граф, anchors, impact, simulate, тесты.
- `feat/api` — DTO, роутеры, тесты API.
- `feat/ui-shell` — layout, тема, навигация, Dashboard (скелет).
- `feat/ui-charts` — графики, LossCounter, ChainPanel.
- `feat/ui-decision` — формы, журнал, Telegram.
- `feat/ai-report` — Gemini+PDF.
- `feat/pitch` — слайды, script.

Мерж: `main`. Каждый merge прогоняет `pytest` + `npm run build`.

### 13.5. Ревью в режиме вибе-кодинга

Не читаем весь код. Проверяем три вещи:

1. **Тесты зелёные** (иначе reject).
2. **На экране цифры сходятся** (визуальная проверка на демо-треке).
3. **Не появилось хардкода** в `frontend/` (`grep -r "1840\|41200\|22120" frontend/src` должен быть пуст).

### 13.6. Работа с ошибками/IT

- Если `uv run pytest` падает → агент сперва правит тесты, только потом код, если тест неправильный.
- Если `npm run build` падает — блокер, не мержим.
- Если сервер падает — в `main.py` обработчик `Exception` пишет в `logs/api.log` и возвращает `{detail}` с кодом 500, но интерфейс не падает.

### 13.7. Работа с контекстом (чтобы агент не тонул)

- Каждый файл ≤ 300 строк.
- Один файл = одна тема (например, `whatif.py` только what-if).
- DTO не дублируют друг друга (все в `schemas.py`).
- Насовсем без `any` в TS.
- Главный принцип: если агент просит много контекста — плохой файл, переписать.

---

<a id="14"></a>
## 14. Порядок работ по шагам (без ролей)

Ниже — задачи, которые можно раздавать агентам. Каждая — 30–90 минут. Порядок — по зависимостям.

### 14.1. Этап 0: Скаффолд (0.5 дня)

**T0.1.** Скрипт `tasks.ps1`: `dev`, `seed`, `test`, `build`, `serve`.
**T0.2.** `backend/pyproject.toml` + `uv sync` + проверка Python 3.14.
**T0.3.** `frontend/` через `npm create vite@latest` и удаление демо-кода; подключить Tailwind v4, `theme.css`, Inter.
**T0.4.** `app/main.py` с `/api/health`, CORS.
**T0.5.** `AGENTS.md`, `.env.example`, `.gitignore`.

**Приёмка:** `uv run pytest` (пусто) зелёный; `npm run dev` открывает страницу; `curl /api/health` отвечает.

### 14.2. Этап 1: Данные и граф (0.5–1 день)

**T1.1.** `core/constants.py`: `COST_PER_DOWNTIME_H=131`, `BASE_WEEKLY_REVENUE`, и т.д.
**T1.2.** `core/anchors.py` + `validate_anchors()`.
**T1.3.** `data/graph.json` по §6 (все 18 узлов, 17 рёбер, 3 path_hint).
**T1.4.** `norms.json`, `seasonality.json` по §5.
**T1.5.** `core/loader.py` — читает `facts`, `norms`, `seasonality`, `graph` с диска.
**T1.6.** `tasks.ps1 seed` — генерирует `facts.json` (seed=42).
**T1.7.** `tests/test_anchors.py`, `tests/test_graph.py` (ацикличен, листья, path_hint длина ≤4).
**T1.8.** `app/data/scenarios/{main,neg,peak}.json` — фикстуры.

**Приёмка:** `pytest test_anchors test_graph` зелёный.

### 14.3. Этап 2: Core-математика (0.5 дня)

**T2.1.** `core/impact.py::delta`. Тест: `delta("hr_operators_s3", +2)` даёт `prod_downtime_l2` ≈ `−6` ч (с curvature) и `fin_margin` ≈ `+?`.
**T2.2.** `core/interpolation.py::interp` + тест на точки 4/5/6.
**T2.3.** `core/economics.py::loss_day`, `unit_economics`.
**T2.4.** `core/forecast.py`; тест: `forecast(47).deficit ≈ 190`.
**T2.5.** `core/simulate.py`; тесты: `simulate(14, [hire]) → +22 120`; `simulate(14, [hire], branch="neg") → verdict ineffective`.

**Приёмка:** все ядровые тесты зелёные.

### 14.4. Этап 3: API (0.5–1 день)

**T3.1.** `schemas.py` — все DTO по §9.
**T3.2.** `api/snapshot.py`, `api/dashboard.py`.
**T3.3.** `api/chain.py`, `api/slices.py`.
**T3.4.** `api/whatif.py`.
**T3.5.** `api/forecast.py`, `api/unit_econ.py`.
**T3.6.** `db.py` + `api/decisions.py`.
**T3.7.** `integrations/jira.py`, `integrations/telegram.py`.
**T3.8.** `api/ai.py` + `integrations/gemini.py`.
**T3.9.** `report/pdf.py` + `api/report.py`.
**T3.10.** `tests/test_api.py` — по DTO.

**Приёмка:** `curl` по всем эндпоинтам отдаёт правильные формы, `pytest` зелёный.

### 14.5. Этап 4: UI каркас (0.5 дня)

**T4.1.** `api/types.ts`, `api/client.ts`, `api/queries.ts`.
**T4.2.** `layout/Header.tsx`, `Section.tsx`, `Modal.tsx`, `Toast.tsx`.
**T4.3.** `store/ui.ts`, `store/demo.ts`.
**T4.4.** `pages/Dashboard.tsx` — общие секции (пустые).
**T4.5.** `lib/format.ts` (BYN, %, склонения, даты).

**Приёмка:** страница открывается, header и пустые секции видны.

### 14.6. Этап 5: UI данные (1 день)

**T5.1.** `KpiCard`, `AlertRow`, `KpiGrid` — данные из `useDashboard`.
**T5.2.** `LossCounter`.
**T5.3.** `chain/ChainBreadcrumbs`, `ChainPanel`, `AiNote`.
**T5.4.** `WhatIfSlider`, `WhatIfTable`, `WhatIfDeltaCards`.
**T5.5.** `ForecastCard`.
**T5.6.** `UnitEconTable`.

**Приёмка:** пользователь видит демо-трек: клик по марже → цепочка → AI / ползунок.

### 14.7. Этап 6: Петля решений (0.5–1 день)

**T6.1.** `DecisionForm` + валидация + toast.
**T6.2.** `JournalTable` + бейджи.
**T6.3.** `NotificationLog` (страница `journal`).
**T6.4.** `BeforeAfterCard` + «А если бы не сработало?».
**T6.5.** `pages/DecisionPage.tsx` по `/decision/:id`.

**Приёмка:** оформленное решение появляется в журнале, подтверждение Telegram видно.

### 14.8. Этап 7: Отчёт и AI (0.5 дня)

**T7.1.** `report/context.py`, `report/pdf.py` + тест PDF.
**T7.2.** `pages/ReportPage.tsx` (кнопка скачать).
**T7.3.** Предзаполнить `data/ai_cache.json` 5-ю сценами.
**T7.4.** `AiNote` UI, `useAi` хук.

**Приёмка:** PDF скачивается и открывается; AI-ответ приходит за < 2 c.

### 14.9. Этап 8: Полировка + питч (1 день)

**T8.1.** Демо-сценарий `lib/demoScript.ts`: подсветки, «дальше».
**T8.2.** Сброс демо (кнопка → сброс state → refetch).
**T8.3.** Мобильный вид (для телефона в Telegram-ссылке).
**T8.4.** Backup: `backup-demo-v2.mp4`, `.zip` репозитория.
**T8.5.** Слайды `pitch/slides.md`, `coverage.md`.
**T8.6.** Репетиция ×3 с таймером.

---

<a id="15"></a>
## 15. Тест-план и Definition of Done

### 15.1. Пирамида

- **Unit (pytest)**: anchors, graph, impact, simulate, forecast, ai_guard, pdf.
- **API (pytest + httpx)**: все эндпоинты, DTO.
- **E2E (ручной)**: демо-трек из 10 шагов, время ≤ 4:00.

### 15.2. Ключевые тесты

```python
# test_anchors.py
def test_loss_effect():
    assert ANCHORS["loss_day_by_ops"][4] - ANCHORS["loss_day_by_ops"][6] == 1580
    assert 14 * 1580 == 22120

# test_api.py
def test_whatif_anchor_points(client):
    for ops, exp in [(4, (14,23,41200,1840)), (5, (8,11,44900,980)), (6, (2,3,47600,260))]:
        r = client.post("/api/whatif", json={"scenario":"main","node_id":"hr_operators_s3","value":ops})
        d = r.json()
        assert (round(d["downtime_h"]), d["sla_orders"], d["revenue_week"], d["loss_day"]) == exp

# test_simulate.py
def test_main_branch():
    res = simulate(14, [hire_decision(2)], branch="main")
    assert abs(res.effect_byn - 22120) <= 1
    assert res.verdict == "effective"

def test_neg_branch():
    res = simulate(14, [hire_decision(2)], branch="neg")
    assert res.verdict == "ineffective"
    assert res.compensating_cause == "equip_lamination_wear"

# test_ai_guard.py
def test_foreign_number_rejected():
    ctx = {"margin": 32, "cost": 1840}
    raw = {"interpretation":"маржа 99%", "root_cause":"x", "recommended_action":"y"}
    ok, reason = validate(raw, ctx)
    assert not ok and "99" in reason
```

### 15.3. DoD (чек-лист защитнику)

- [ ] `uv run pytest -q` — зелёный.
- [ ] `npm run build` — без ошибок TS.
- [ ] Демо-путь (10 шагов) проходит за ≤ 4:00 на чистом state.
- [ ] `grep -rE "1840|41200|22120" frontend/src` — пусто.
- [ ] Chrome DevTools: Network — ни одного запроса наружу (кроме api.telegram.org / generativelanguage.googleapis.com при живом режиме). Offline-режим — вообще чист (кэш).
- [ ] `curl /api/health` — 200.
- [ ] PDF открывается в Adobe Reader (не только в Chrome).
- [ ] Телефон получает сообщение; при отсутствии сети — журнал отправок.

---

<a id="16"></a>
## 16. Фолбэки, риски, демо-день

### 16.1. Фолбэки (расширено)

| Риск | Вероятность | Действие |
|---|---|---|
| Нет интернета | высокая | `OFFLINE_MODE=true`, весь UI на localhost, Gemini из кэша, Telegram → журнал отправок |
| Telegram токен пуст/заблокирован | средняя | `status=skipped_no_token`, journal + скринкаст телефона |
| Gemini таймаут/брак | средняя | timeout 5, validator, fallback-шаблон |
| Python 3.14 + reportlab без wheel | средняя | `uv python pin 3.12`, пересборка |
| Граф разошёлся с UI | низкая | Один источник (API) + тесты |
| Числа не сходятся (побились) | низкая | `test_anchors`, `test_simulate` |
| Демо упало | средняя | `backup-demo-v2.mp4` на двух флешках + `.zip` репо |
| Чужие цифры в AI | средняя | `test_ai_guard`, predcache |
| Проектор/HDMI | низкая | Адаптеры, второй ноут |
| «Данные синтетика?» | 100% | Слайд «калибровка по CEWE/Shutterfly + адаптер под реальные данные §2.3» |

### 16.2. Демо-день (хронометраж 3:40)

| # | Время | Что | Экран |
|---|---|---|---|
| 1 | 0:00–0:15 | Боль: «собираем причину по трём Excel — неделя» | слайд |
| 2 | 0:15–0:35 | Dashboard: маржа −10 п.п., −1 840 BYN/сут, тикает | Dashboard |
| 3 | 0:35–0:55 | Клик по алерту → кросс-фильтрация 4 домена | Dashboard |
| 4 | 0:55–1:25 | Drill-down → «нехватка 2 брошюровщиков №3» + AI | ChainPanel |
| 5 | 1:25–1:55 | Ползунок 4→6, таблица | WhatIf |
| 6 | 1:55–2:20 | «Оформить» → Telegram на телефоне | Form → toast |
| 7 | 2:20–2:50 | «⏩ +14 дней» → +22 120 BYN, verdict | BeforeAfter |
| 8 | 2:50–3:05 | «А если бы не сработало» — негативная ветка | NegativeBranch |
| 9 | 3:05–3:25 | Превентивная карточка пика | ForecastCard |
| 10 | 3:25–3:40 | Executive Summary PDF + слайд покрытия | PDF |

### 16.3. Back-up video

Запись экрана 1080p, без звука (питч — живьём), с POP-ами на ключевых цифрах. 2 флешки, ноут-дубль.

---

<a id="17"></a>
## 17. Питч и покрытие ТЗ

### 17.1. Слайды

1. Проблема (Excel-хроника).
2. Решение: петля.
3. Скрин: дашборд.
4. Скрин: drill-down.
5. Следующий шаг: What-If.
6. Telegram.
7. Было → стало.
8. Предиктив.
9. Данные и честность (синтетика, калибровка, адаптер).
10. Roadmap.
11. Покрытие ТЗ (галочки).

### 17.2. `coverage.md` (шаблон)

```
☑ Визуализация KPI по 4 доменам
☑ Алертинг с ценой дня
☑ Drill-down до причины
☑ Кросс-фильтрация (1 связка)
☑ What-If
☑ Cost of Inaction
☑ Action-модуль + журнал
☑ Telegram
☑ Проверка «было → стало»
☑ Машина времени
☑ Негативная ветка
☑ Предиктив пика
☑ Executive Summary PDF
☑ AI-интерпретация с анти-галлюцинацией
☑ Адаптер под реальные данные
☑ Демо-видео backup
```

---

<a id="18"></a>
## 18. Открытые вопросы (нужно решить)

1. **Расхождение 1 840 / 260 / 22 120** — решено в §2: якоря в `ANCHORS`, физическая константа `131 BYN/ч`. Нужно только решение по слайду «с точностью до округления».
2. **Прогноз пика**: расчёт `917 × 1.004 × 1.35 = 1 242` → округление до десятков = **1 240** (как в ТЗ). Отдельного решения не требуется.
3. **Потери в пике 1 183 vs 1 180** — выбрал **округление до 1 180** на экране (или 1 183 — на выбор).
4. **WeasyPrint vs reportlab** — выбрал **reportlab** (Windows без GTK).
5. **SQLite vs JSON** для журнала — выбрал **SQLite** (надёжнее на демо, тривиально бэкапится).
6. **Механика «те же веса»** — выбрал **интерполяция по anchors** для ползунка, **граф** — для объяснения; это честно и тестируемо. На вопрос «одна математика?» — ответ: «одна модель, одна константа (131 BYN/ч); ползунок — калибровочная кривая из трёх точек, проверяется тестом».
7. **Открытый вопрос: подключить ли в what-if** «ремонт ламинатора» → ползунок уже на `equip`? Пока **нет**, в roadmap.
8. **Место для `demo_script` (автопрокрутка)** — добавить, если будет время; не критично.

---

## Итог

Единственное, что понадобится для успеха: **один источник чисел** (`ANCHORS` + `core/`), **тесты, которые читают эти числа**, и **UI, который только отрисовывает**. Всё «умное» (AI, PDF, Telegram) — за фолбэками. Тогда даже неудачный демо-прогон можно отыграть по видео, и цифры на экране никогда не разойдутся.

Суммарная оценка ≈ 140 ч, доступно 160 ч; буфер 20 ч — вкладываем в тесты (T1–T2) и backup (T8).
