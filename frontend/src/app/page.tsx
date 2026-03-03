"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ImageUploader } from "@/components/ImageUploader";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";

export default function UploadPage() {
  const router = useRouter();
  const setSession = useAppStore((s) => s.setSession);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const result = await api.uploadPhoto(file);
      setSession(result.session_id, result.image_url);
      router.push("/style");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-12">
      <div className="w-full max-w-lg mx-auto text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900">AI Home Styling</h1>
        <p className="text-gray-500 mt-2">
          Upload a photo of your room and see it transformed
        </p>
      </div>

      <ImageUploader onUpload={handleUpload} isUploading={isUploading} />

      {error && <p className="mt-4 text-red-600 text-sm">{error}</p>}

      <div className="w-full max-w-lg mt-12">
        <p className="text-sm text-gray-400 text-center mb-4">
          See what AI styling can do
        </p>
        <div className="grid grid-cols-2 gap-3">
          {[
            { id: 1, url: "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80" },
            { id: 2, url: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=800&q=80" },
            { id: 3, url: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80" },
            { id: 4, url: "https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&w=800&q=80" }
          ].map((item) => (
            <div
              key={item.id}
              className="aspect-[4/3] rounded-xl overflow-hidden relative"
            >
              <img src={item.url} alt={`Example ${item.id}`} className="object-cover w-full h-full" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
