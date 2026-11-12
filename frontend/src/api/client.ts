/** Fetch-клиент с нормализацией ошибок (§9.2 Readme.md). */
import { useDemoStore } from "../store/demo";

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string, message?: string) {
    super(message ?? `HTTP ${status}: ${detail}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }

  static fromResponse(res: Response, body: unknown): ApiError {
    const detail = (body as { detail?: string } | null)?.detail ?? res.statusText;
    return new ApiError(res.status, String(detail));
  }
}

const NO_BODY = { method: "GET", headers: { "Content-Type": "application/json" } as HeadersInit };

function buildUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return path.startsWith("/") ? path : `/${path}`;
}

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  if (!text) return {} as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(res.status, "Некорректный JSON в ответе");
  }
}

function headersWith(extra?: HeadersInit): HeadersInit {
  const state = useDemoStore.getState();
  
  // Создаём базовые заголовки
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  // Добавляем заголовки RBAC только если они есть
  if (state.role) {
    headers["X-Demo-Role"] = state.role;
  }
  if (state.dept) {
    headers["X-Demo-Dept"] = state.dept;
  }
  
  // Добавляем дополнительные заголовки из extra
  if (extra) {
    // Преобразуем HeadersInit в Record<string, string>
    if (Array.isArray(extra)) {
      // Если это массив пар [key, value]
      extra.forEach(([key, value]) => {
        headers[key] = value;
      });
    } else if (extra instanceof Headers) {
      // Если это объект Headers
      extra.forEach((value, key) => {
        headers[key] = value;
      });
    } else {
      // Если это обычный объект
      Object.entries(extra).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          headers[key] = String(value);
        }
      });
    }
  }
  
  return headers;
}

export async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(buildUrl(path), { ...NO_BODY, ...init, headers: headersWith(init?.headers) });
  if (!res.ok) {
    const body = await parseJson<{ detail?: string }>(res).catch(() => ({}));
    throw ApiError.fromResponse(res, body);
  }
  return parseJson<T>(res);
}

export async function postJson<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: "POST",
    headers: headersWith(init?.headers),
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const bodyErr = await parseJson<{ detail?: string }>(res).catch(() => ({}));
    throw ApiError.fromResponse(res, bodyErr);
  }
  return parseJson<T>(res);
}