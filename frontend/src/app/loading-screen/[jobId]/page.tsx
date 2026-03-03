"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { RenderProgress } from "@/components/RenderProgress";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";

export default function LoadingPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;
  const { sessionId, styleId, setRenders } = useAppStore();

  const { data: jobStatus } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.getJobStatus(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") return false;
      return 2000;
    },
  });

  useEffect(() => {
    if (jobStatus?.status === "completed" && sessionId) {
      if (jobStatus.renders) {
        setRenders(jobStatus.renders, jobStatus.bundle_id || "");
      }
      router.push(`/gallery/${sessionId}`);
    }
  }, [jobStatus, sessionId, router, setRenders]);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="absolute inset-0 opacity-10 bg-gradient-to-b from-gray-200 to-white" />

      <div className="relative z-10">
        {jobStatus?.status === "failed" ? (
          <div className="text-center">
            <p className="text-red-600 font-medium">Something went wrong</p>
            <p className="text-gray-500 text-sm mt-2">
              {jobStatus.error || "Please try again"}
            </p>
            <button
              onClick={() => router.push("/")}
              className="mt-4 bg-blue-600 text-white py-2 px-6 rounded-xl font-medium hover:bg-blue-700 transition"
            >
              Try again
            </button>
          </div>
        ) : (
          <RenderProgress status={jobStatus?.status || "analyzing"} />
        )}
      </div>
    </main>
  );
}
