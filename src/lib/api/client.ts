import type { ApiErrorBody } from "@/types/api";

export class ApiError extends Error {
  status: number;
  details?: Record<string, string[]>;

  constructor(message: string, status: number, details?: Record<string, string[]>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  if (!baseUrl) {
    throw new ApiError("Online submission is not configured yet. Please call or email the studio.", 503);
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError("We could not reach the server. Please try again or contact the studio directly.", 0);
  }

  const payload = (await response.json().catch(() => null)) as ApiErrorBody | T | null;
  if (!response.ok) {
    const error = payload && typeof payload === "object" && "message" in payload ? payload : null;
    throw new ApiError(
      error?.message ?? "Your request could not be completed. Please try again.",
      response.status,
      error && "errors" in error ? error.errors : undefined,
    );
  }
  if (payload === null) throw new ApiError("The server returned an empty response.", response.status);
  return payload as T;
}
