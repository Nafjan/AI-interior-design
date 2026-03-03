"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";
import { HotspotOverlay } from "@/components/HotspotOverlay";
import { ProductCard } from "@/components/ProductCard";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import type { Hotspot, ProductSummary } from "@/types";

export default function GalleryPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { renders, styleId, setProducts } = useAppStore();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedProduct, setSelectedProduct] =
    useState<ProductSummary | null>(null);

  // Fetch the product bundle
  const { data: bundle } = useQuery({
    queryKey: ["bundle", styleId],
    queryFn: () => api.getBundle(styleId || "modern"),
    enabled: !!styleId,
  });

  useEffect(() => {
    if (bundle) {
      setProducts(bundle.products, bundle.total_price_sar);
    }
  }, [bundle, setProducts]);

  const products = bundle?.products || [];
  const productMap = Object.fromEntries(products.map((p) => [p.id, p]));
  const currentRender = renders[currentIndex];

  const handleHotspotClick = (hotspot: Hotspot) => {
    const product = productMap[hotspot.product_id];
    if (product) {
      setSelectedProduct(product);
    }
  };

  const handlePrev = () =>
    setCurrentIndex((i) => (i > 0 ? i - 1 : renders.length - 1));
  const handleNext = () =>
    setCurrentIndex((i) => (i < renders.length - 1 ? i + 1 : 0));

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Render carousel */}
      <div className="relative w-full aspect-[4/3] bg-gradient-to-br from-gray-200 to-gray-300 overflow-hidden">
        {currentRender?.url ? (
          <Image
            src={currentRender.url}
            alt={`Styled room variant ${currentIndex + 1}`}
            fill
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-gray-400">
              Styled Room - Variant {currentIndex + 1}
            </span>
          </div>
        )}

        {currentRender && (
          <HotspotOverlay
            key={currentRender.url}
            hotspots={currentRender.hotspots}
            onHotspotClick={handleHotspotClick}
          />
        )}

        {renders.length > 1 && (
          <>
            <button
              onClick={handlePrev}
              className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center shadow-md hover:bg-white transition"
            >
              <ChevronLeft size={20} />
            </button>
            <button
              onClick={handleNext}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center shadow-md hover:bg-white transition"
            >
              <ChevronRight size={20} />
            </button>
          </>
        )}

        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
          {renders.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i)}
              className={`w-2.5 h-2.5 rounded-full transition-colors ${
                i === currentIndex ? "bg-white" : "bg-white/50"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Product strip */}
      <div className="px-4 py-6">
        <h2 className="font-semibold text-gray-900 mb-3">
          Products in this room
        </h2>
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4">
          {products.map((product) => (
            <button
              key={product.id}
              onClick={() => setSelectedProduct(product)}
              className="flex-shrink-0 w-32 text-left"
            >
              <div className="w-32 h-32 bg-gray-100 rounded-xl flex items-center justify-center overflow-hidden relative">
                {product.image_url ? (
                  <Image
                    src={product.image_url}
                    alt={product.name}
                    fill
                    className="object-contain p-1"
                    unoptimized
                  />
                ) : (
                  <span className="text-xs text-gray-400 capitalize">
                    {product.category}
                  </span>
                )}
              </div>
              <p className="text-xs font-medium text-gray-900 mt-2 truncate">
                {product.name}
              </p>
              <p className="text-xs text-gray-500">
                SAR {product.price_sar.toLocaleString()}
              </p>
            </button>
          ))}
        </div>

        {bundle && (
          <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
            <span className="text-sm text-gray-500">Total bundle price</span>
            <span className="font-bold text-lg">
              SAR {bundle.total_price_sar.toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {/* Product card overlay */}
      <AnimatePresence>
        {selectedProduct && (
          <>
            <div
              className="fixed inset-0 bg-black/30 z-40"
              onClick={() => setSelectedProduct(null)}
            />
            <ProductCard
              product={selectedProduct}
              onClose={() => setSelectedProduct(null)}
              onViewDetails={() => {
                // Track click
                api.trackEvent(sessionId, "product_link_clicked", selectedProduct.id);
              }}
            />
          </>
        )}
      </AnimatePresence>
    </main>
  );
}
