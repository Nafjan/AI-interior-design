"use client";

import { motion } from "framer-motion";
import { ExternalLink, X } from "lucide-react";
import Image from "next/image";
import type { ProductSummary } from "@/types";

interface ProductCardProps {
  product: ProductSummary;
  productUrl?: string;
  onClose: () => void;
  onViewDetails: (productId: string) => void;
}

export function ProductCard({
  product,
  onClose,
  onViewDetails,
}: ProductCardProps) {
  return (
    <motion.div
      initial={{ y: "100%" }}
      animate={{ y: 0 }}
      exit={{ y: "100%" }}
      transition={{ type: "spring", damping: 25, stiffness: 300 }}
      className="fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl p-6 z-50 max-w-lg mx-auto"
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
      >
        <X size={20} />
      </button>

      <div className="flex gap-4">
        <div className="w-24 h-24 bg-gray-100 rounded-xl flex-shrink-0 overflow-hidden relative">
          {product.image_url ? (
            <Image
              src={product.image_url}
              alt={product.name}
              fill
              className="object-contain p-1"
              unoptimized
            />
          ) : (
            <div className="flex items-center justify-center w-full h-full">
              <span className="text-xs text-gray-400">{product.category}</span>
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">
            {product.name}
          </h3>
          <p className="text-sm text-gray-500 capitalize">
            {product.supplier}
          </p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            SAR {product.price_sar.toLocaleString()}
          </p>
        </div>
      </div>

      <div className="mt-4 flex gap-3">
        <button
          onClick={() => {
            onViewDetails(product.id);
            if (product.product_url) {
              window.open(product.product_url, "_blank");
            }
          }}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-blue-700 transition"
        >
          View on {product.supplier.toLowerCase() === "ikea" ? "IKEA" : product.supplier.toLowerCase() === "west elm" ? "West Elm" : "Store"}
          <ExternalLink size={16} />
        </button>
      </div>
    </motion.div>
  );
}
