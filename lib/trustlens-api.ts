import type { TrustLensResult } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_TRUSTLENS_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8080";

async function parseResponse(response: Response): Promise<TrustLensResult> {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.detail || `TrustLens API failed with ${response.status}`;
    throw new Error(message);
  }
  return body as TrustLensResult;
}

export async function analyzeText(input: {
  message: string;
  language: string;
  signal?: AbortSignal;
}): Promise<TrustLensResult> {
  const response = await fetch(`${API_BASE_URL}/v1/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: input.message, language: input.language }),
    signal: input.signal,
  });
  return parseResponse(response);
}

export async function analyzeMultipart(input: {
  message: string;
  language: string;
  screenshot: File;
  signal?: AbortSignal;
}): Promise<TrustLensResult> {
  const formData = new FormData();
  formData.append("message", input.message);
  formData.append("language", input.language);
  formData.append("screenshot", input.screenshot);

  const response = await fetch(`${API_BASE_URL}/v1/analyze/multipart`, {
    method: "POST",
    body: formData,
    signal: input.signal,
  });
  return parseResponse(response);
}
