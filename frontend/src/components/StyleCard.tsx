"use client";

import { Check } from "lucide-react";
import type { Style } from "@/types";

interface StyleCardProps {
  style: Style;
  selected: boolean;
  onSelect: (styleId: string) => void;
}

export function StyleCard({ style, selected, onSelect }: StyleCardProps) {
  return (
    <button
      onClick={() => onSelect(style.id)}
      className={`relative w-full rounded-2xl overflow-hidden border-2 transition-all text-left ${
        selected
          ? "border-blue-600 ring-2 ring-blue-200"
          : "border-gray-200 hover:border-gray-300"
      }`}
    >
      <div className="aspect-[16/10] bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
        {style.thumbnail_url ? (
          <img 
            src={style.thumbnail_url} 
            alt={`${style.name} style preview`} 
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-4xl text-gray-400">
              {style.id === "modern" ? "M" : "m"}
            </span>
          </div>
        )}
      </div>

      <div className="p-4 text-left">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-lg">{style.name}</h3>
          {selected && (
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
              <Check size={14} className="text-white" />
            </div>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">{style.description}</p>
      </div>
    </button>
  );
}
