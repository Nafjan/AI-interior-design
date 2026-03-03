"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StyleCard } from "@/components/StyleCard";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";

export default function StylePickerPage() {
  const router = useRouter();
  const { sessionId, setStyle, setJob } = useAppStore();
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: styles } = useQuery({
    queryKey: ["styles"],
    queryFn: () => api.getStyles(),
  });

  const handleGenerate = async () => {
    if (!selectedStyle || !sessionId) {
      if (!sessionId) router.push("/");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      setStyle(selectedStyle);
      const result = await api.triggerGeneration(sessionId, selectedStyle);
      setJob(result.job_id);
      router.push(`/loading-screen/${result.job_id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to start generation"
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col px-4 py-8">
      <div className="w-full max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-gray-900">Choose a style</h1>
        <p className="text-gray-500 mt-1">
          Pick a style for your room transformation
        </p>

        <div className="mt-6 space-y-4">
          {(styles || []).map((style) => (
            <StyleCard
              key={style.id}
              style={style}
              selected={selectedStyle === style.id}
              onSelect={setSelectedStyle}
            />
          ))}
        </div>

        <p className="text-sm text-gray-400 text-center mt-6">
          Budget: SAR 8,000 - 15,000 (mid range)
        </p>

        {error && (
          <p className="mt-4 text-red-600 text-sm text-center">{error}</p>
        )}

        <button
          onClick={handleGenerate}
          disabled={!selectedStyle || isGenerating}
          className="w-full mt-6 bg-blue-600 text-white py-3.5 px-6 rounded-xl font-medium text-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {isGenerating ? "Starting..." : "Style my room"}
        </button>
      </div>
    </main>
  );
}
