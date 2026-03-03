export interface Style {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
}

export interface UploadResponse {
  session_id: string;
  image_url: string;
  room_type: string | null;
  created_at: string;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
}

export interface Hotspot {
  product_id: string;
  x_pct: number;
  y_pct: number;
  category: string;
}

export interface RenderResult {
  url: string;
  hotspots: Hotspot[];
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "analyzing" | "rendering" | "mapping" | "completed" | "failed";
  progress: string | null;
  renders: RenderResult[] | null;
  bundle_id: string | null;
  error: string | null;
}

export interface ProductSummary {
  id: string;
  name: string;
  category: string;
  price_sar: number;
  image_url: string;
  supplier: string;
  product_url: string;
}

export interface Product extends ProductSummary {
  name_ar: string | null;
  image_urls: string[];
  dimensions_cm: Record<string, number> | null;
  product_url: string;
  style_tags: string[];
}

export interface ProductBundle {
  id: string;
  name: string;
  style: string;
  budget_tier: string;
  products: ProductSummary[];
  total_price_sar: number;
}
