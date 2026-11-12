# ADR 0004: Маршрутизация фронтенда — react-router

Статус: Принято
Дата: 2026-11-08
Контекст задачи: PLAN.md, этап 4 (B1), задачи T4.2–T4.4

> Нумерация: `0003` уже занят ADR о миграции AI-провайдера на DeepSeek
> (`docs/adr/0003-ai-provider-deepseek.md`, A3, 07.11.2026), поэтому решение по
> роутеру получило номер `0004`.

## Контекст
Readme §4.2 и §10 задают приложению несколько URL-экранов:
`/` (Dashboard), `/journal` (журнал уведомлений), `/report` (Executive PDF),
`/decision/:id` (карточка решения по диплинку из Telegram), `/devkit` (служебный стенд состояний).
Дополнительно нужны:
- прямые ссылки из Telegram-бота на конкретное решение (`/decision/:id`);
- ленивая загрузка страниц (code-splitting), чтобы стартовый бандл оставался маленьким;
- единая точка входа, совместимая с уже существующим `QueryClientProvider` (T4.1);
- фолбэк для окружений Telegram WebApp без рабочего History API.

## Решение
Используем **react-router** (в `package.json` зафиксирован `react-router@^8.5.1`) и его
**Data Router API**: `createBrowserRouter` + `RouterProvider`.

## Обоснование выбора
- **Один пакет.** В react-router ≥ 7 нет разделения на `react-router-dom`; всё нужное
  (`RouterProvider`, `createBrowserRouter`, `createHashRouter`, `Outlet`, `NavLink`,
  `useNavigate`, `useSearchParams`, `RouteObject`) экспортируется из `react-router`.
- **Маршруты как данные.** Массив `RouteObject[]` удобно расширять (вложенные лейауты,
  `lazy`, `errorElement`) и типизировать; `App.tsx` остаётся тонким.
- **Готовность к T5–T6.** Data Router совместим с TanStack Query (загрузка данных остаётся
  на хуках запросов, роутер отвечает только за навигацию) и не навязывает свои загрузчики.
- **Code-splitting.** Каждая страница подключается через `React.lazy` и оборачивается в
  `Suspense` с общим скелетоном — `/devkit`, `/report`, `/decision/:id` не попадают в
  стартовый чанк Dashboard.
- **Обратная совместимость.** `createMemoryRouter` доступен для будущих тестов страниц.

## Фолбэк: hash-роутер
Если `import.meta.env.VITE_HASH_ROUTER === "1"`, вместо `createBrowserRouter` создаётся
`createHashRouter`. Это покрывает Telegram WebApp-окружения, где `history.pushState`
может быть недоступен. Логика выбора вынесена в `src/routes.tsx`.

## Структура маршрутов (`src/routes.tsx`)
```tsx
export const routes: RouteObject[] = [
  { path: "/", element: <Dashboard /> },
  { path: "/journal", element: <JournalPage /> },
  { path: "/report", element: <ReportPage /> },
  { path: "/decision/:id", element: <DecisionPage /> },
  { path: "/devkit", element: <DevKit /> },
  { path: "*", element: <Navigate to="/" replace /> },
];

export const router = useHashRouter ? createHashRouter(routes) : createBrowserRouter(routes);
```

## Интеграция в `App.tsx`
`App.tsx` сохраняет установку темы (`useEffect` + `applyThemeAttrs`) и разметку
шапки (`Header`), а контент страниц рендерит через `RouterProvider`.
`Header` и `ThemeSwitcher` не изменяются (ограничение задачи).

## Последствия
- Зависимость: `react-router@^8.5.1` (единственная новая в B1).
- `App.tsx` делегирует маршрутизацию роутеру, но сохраняет общую шапку и фон.
- Типы маршрутов: `RouteObject` из `react-router`.
- Версия в Readme стр.176/215 (`react-router@7`) расходится с фактически установленной
  (`^8.5.1`). Публичного API, используемого приложением, изменение не затрагивает;
  расхождение зафиксировано в теле коммита B1.