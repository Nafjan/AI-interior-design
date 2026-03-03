import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { RenderResult, ProductSummary } from "@/types";

interface AppState {
  sessionId: string | null;
  imageUrl: string | null;
  styleId: string | null;
  jobId: string | null;
  renders: RenderResult[];
  bundleId: string | null;
  products: ProductSummary[];
  totalPrice: number;

  setSession: (sessionId: string, imageUrl: string) => void;
  setStyle: (styleId: string) => void;
  setJob: (jobId: string) => void;
  setRenders: (renders: RenderResult[], bundleId: string) => void;
  setProducts: (products: ProductSummary[], totalPrice: number) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null as string | null,
  imageUrl: null as string | null,
  styleId: null as string | null,
  jobId: null as string | null,
  renders: [] as RenderResult[],
  bundleId: null as string | null,
  products: [] as ProductSummary[],
  totalPrice: 0,
};

export const useAppStore = create(
  persist<AppState>(
    (set) => ({
      ...initialState,
      setSession: (sessionId, imageUrl) => set({ sessionId, imageUrl }),
      setStyle: (styleId) => set({ styleId }),
      setJob: (jobId) => set({ jobId }),
      setRenders: (renders, bundleId) => set({ renders, bundleId }),
      setProducts: (products, totalPrice) => set({ products, totalPrice }),
      reset: () => set(initialState),
    }),
    { name: "ai-styling-session" }
  )
);
