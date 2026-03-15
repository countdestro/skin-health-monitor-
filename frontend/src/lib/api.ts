import type {
  ApiEnvelope,
  AnalyseRequest,
  AnalysisResult,
  HistoryResponse,
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ANALYSE_TIMEOUT_MS = 15000;

export async function analyseImage(
  imageBase64: string,
  sessionId: string
): Promise<ApiEnvelope<AnalysisResult>> {
  const body: AnalyseRequest = {
    image_b64: imageBase64,
    session_id: sessionId,
    timestamp: new Date().toISOString(),
  };
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ANALYSE_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE}/analyse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const json = (await res.json()) as ApiEnvelope<AnalysisResult>;
    if (!res.ok) {
      return {
        success: false,
        code: json.code ?? "ERROR",
        message: json.message ?? "Request failed",
        data: json.data,
      };
    }
    return json;
  } catch (e) {
    if ((e as Error).name === "AbortError") {
      return {
        success: false,
        code: "TIMEOUT",
        message: "Request took too long. Please try again.",
      };
    }
    return {
      success: false,
      code: "NETWORK_ERROR",
      message: (e as Error).message || "Network error",
    };
  } finally {
    clearTimeout(timeout);
  }
}

export async function getSession(sessionId: string): Promise<ApiEnvelope<AnalysisResult>> {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  return res.json();
}

export async function getHistory(
  userId: string,
  page = 1
): Promise<ApiEnvelope<HistoryResponse>> {
  const res = await fetch(`${API_BASE}/history/${userId}?page=${page}`);
  return res.json();
}
