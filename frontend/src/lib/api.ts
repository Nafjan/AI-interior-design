import type {
  GenerateResponse,
  JobStatus,
  Product,
  ProductBundle,
  Style,
  UploadResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Upload
  async uploadPhoto(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Upload failed");
    }

    return res.json();
  },

  // Styles
  async getStyles(): Promise<Style[]> {
    return fetchApi("/api/styles");
  },

  // Generate
  async triggerGeneration(sessionId: string, styleId: string): Promise<GenerateResponse> {
    return fetchApi("/api/generate", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, style_id: styleId }),
    });
  },

  async getJobStatus(jobId: string): Promise<JobStatus> {
    return fetchApi(`/api/generate/${jobId}`);
  },

  // Products
  async getBundle(styleId: string): Promise<ProductBundle> {
    return fetchApi(`/api/bundles/${styleId}`);
  },

  async getProduct(productId: string): Promise<Product> {
    return fetchApi(`/api/products/${productId}`);
  },

  // Analytics
  async trackEvent(
    sessionId: string,
    eventType: string,
    productId?: string,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    await fetchApi("/api/analytics/event", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        event_type: eventType,
        product_id: productId || null,
        metadata: metadata || null,
      }),
    });
  },
};
