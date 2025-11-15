const DEFAULT_BASE_URL = "http://localhost:8000";

export const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL ?? DEFAULT_BASE_URL;

export async function forwardToBackend(path: string, init?: RequestInit) {
  const response = await fetch(`${BACKEND_BASE_URL}${path}`, init);
  const payload = await parseJsonResponse(response);
  return { response, payload };
}

export async function parseJsonResponse(response: Response) {
  try {
    return await response.json();
  } catch {
    return { message: "Unexpected backend response" };
  }
}
