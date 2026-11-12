/** Единый рендер 4 состояний запроса: skeleton / error(+повтор) / empty / success.
 *  Данные приходят из TanStack Query — компоненты не ходят в сеть сами (§10.2, T5.x).
 */
import type { ReactNode } from "react";
import type { UseQueryResult } from "@tanstack/react-query";

/** Плейсхолдер загрузки (skeleton) — нейтральные полосы на panel-2. */
export function SkeletonLines({ rows = 3 }: { rows?: number }) {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-4"
          style={{
            width: i % 2 === 0 ? "90%" : "65%",
            background: "var(--panel-2)",
            borderRadius: "var(--radius)",
          }}
        />
      ))}
    </div>
  );
}

/** Кнопка повтора запроса при ошибке. */
function RetryButton({ onRetry }: { onRetry: () => void }) {
  return (
    <button
      type="button"
      className="tag"
      style={{ color: "var(--alert)", cursor: "pointer" }}
      onClick={onRetry}
    >
      ПОВТОРИТЬ
    </button>
  );
}

export interface AsyncStateProps<T> {
  /** Результат useQuery (или useMutation-подобный объект с data/status). */
  query: UseQueryResult<T, Error>;
  /** Условие «данных нет»; по умолчанию undefined → пусто не бывает. */
  isEmpty?: (data: T) => boolean;
  /** Сколько строк скелетона рисовать. */
  skeletonRows?: number;
  /** Текст пустого состояния. */
  emptyText?: string;
  /** Рендер успешного состояния. */
  children: (data: T) => ReactNode;
}

export function AsyncState<T>({
  query,
  isEmpty,
  skeletonRows = 3,
  emptyText = "Нет данных",
  children,
}: AsyncStateProps<T>) {
  if (query.isPending) {
    return <SkeletonLines rows={skeletonRows} />;
  }

  if (query.isError) {
    return (
      <div className="flex flex-col items-start gap-2">
        <p className="mono text-sm" style={{ color: "var(--alert)" }}>
          {query.error.message || "Не удалось загрузить данные"}
        </p>
        <RetryButton onRetry={() => void query.refetch()} />
      </div>
    );
  }

  const data = query.data as T;
  if (isEmpty?.(data)) {
    return (
      <p className="mono text-sm" style={{ color: "var(--muted)" }}>
        {emptyText}
      </p>
    );
  }

  return <>{children(data)}</>;
}
