"use client";

import { motion } from "framer-motion";
import type { Hotspot } from "@/types";

interface HotspotOverlayProps {
  hotspots: Hotspot[];
  onHotspotClick: (hotspot: Hotspot) => void;
}

export function HotspotOverlay({
  hotspots,
  onHotspotClick,
}: HotspotOverlayProps) {
  return (
    <div className="absolute inset-0">
      {hotspots.map((hotspot, index) => (
        <motion.button
          key={`${hotspot.product_id}-${index}`}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5 + index * 0.15, type: "spring" }}
          onClick={() => onHotspotClick(hotspot)}
          className="absolute w-10 h-10 -ml-5 -mt-5 group"
          style={{
            left: `${hotspot.x_pct}%`,
            top: `${hotspot.y_pct}%`,
          }}
        >
          {/* Pulse ring */}
          <span className="absolute inset-0 rounded-full bg-white/30 animate-ping" />
          {/* Dot */}
          <span className="relative block w-full h-full rounded-full bg-white border-2 border-blue-600 shadow-lg group-hover:bg-blue-50 transition-colors">
            <span className="absolute inset-2 rounded-full bg-blue-600" />
          </span>
        </motion.button>
      ))}
    </div>
  );
}
