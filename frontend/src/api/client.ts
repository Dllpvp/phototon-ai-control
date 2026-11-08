/** Fetch-клиент с нормализацией ошибок (§9.2 Readme.md). */

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
  // API проксируется через vite: /api/* -> http://127.0.0.1:8000/api/*
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
  return { "Content-Type": "application/json", ...extra };
}

/** GET с автоматическим парсингом JSON и броском ApiError. */
export async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(buildUrl(path), { ...NO_BODY, ...init, headers: headersWith(init?.headers) });
  if (!res.ok) {
    const body = await parseJson<{ detail?: string }>(res).catch(() => ({}));
    throw ApiError.fromResponse(res, body);
  }
  return parseJson<T>(res);
}

/** POST с JSON-телом. */
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