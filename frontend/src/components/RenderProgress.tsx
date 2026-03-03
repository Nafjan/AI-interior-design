"use client";

import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";

interface RenderProgressProps {
  status: string;
}

const PHASES = [
  { key: "analyzing", label: "Analyzing your room" },
  { key: "rendering", label: "Styling your room" },
  { key: "mapping", label: "Finding products" },
];

export function RenderProgress({ status }: RenderProgressProps) {
  const currentIndex = PHASES.findIndex((p) => p.key === status);

  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-sm mx-auto">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full"
      />

      <div className="w-full space-y-4">
        {PHASES.map((phase, index) => {
          const isComplete = index < currentIndex || status === "completed";
          const isActive = index === currentIndex;

          return (
            <motion.div
              key={phase.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.3 }}
              className="flex items-center gap-3"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                  isComplete
                    ? "bg-green-100"
                    : isActive
                      ? "bg-blue-100"
                      : "bg-gray-100"
                }`}
              >
                {isComplete ? (
                  <Check size={16} className="text-green-600" />
                ) : isActive ? (
                  <Loader2
                    size={16}
                    className="text-blue-600 animate-spin"
                  />
                ) : (
                  <div className="w-2 h-2 bg-gray-300 rounded-full" />
                )}
              </div>
              <span
                className={`text-sm font-medium ${
                  isComplete
                    ? "text-green-700"
                    : isActive
                      ? "text-blue-700"
                      : "text-gray-400"
                }`}
              >
                {phase.label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
