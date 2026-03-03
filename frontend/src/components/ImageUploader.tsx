"use client";

import { Upload, Camera, X } from "lucide-react";
import Image from "next/image";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

interface ImageUploaderProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export function ImageUploader({ onUpload, isUploading }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
      "image/heic": [".heic"],
    },
    maxSize: 20 * 1024 * 1024,
    multiple: false,
  });

  const clearPreview = () => {
    setPreview(null);
    setSelectedFile(null);
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  if (preview && selectedFile) {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-full max-w-md aspect-[4/3] rounded-xl overflow-hidden">
          <Image
            src={preview}
            alt="Room preview"
            fill
            className="object-cover"
          />
          <button
            onClick={clearPreview}
            className="absolute top-3 right-3 bg-black/50 text-white rounded-full p-1.5 hover:bg-black/70 transition"
          >
            <X size={18} />
          </button>
        </div>
        <button
          onClick={handleSubmit}
          disabled={isUploading}
          className="w-full max-w-md bg-blue-600 text-white py-3 px-6 rounded-xl font-medium text-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {isUploading ? "Uploading..." : "Continue"}
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`w-full max-w-md mx-auto border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
        isDragActive
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
          {isDragActive ? (
            <Upload className="text-blue-600" size={28} />
          ) : (
            <Camera className="text-blue-600" size={28} />
          )}
        </div>
        <div>
          <p className="text-lg font-medium text-gray-900">
            Upload your room
          </p>
          <p className="text-sm text-gray-500 mt-1">
            JPEG, PNG, or HEIC up to 20MB
          </p>
        </div>
      </div>
    </div>
  );
}
