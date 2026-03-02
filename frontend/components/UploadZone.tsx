"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export default function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const file = e.dataTransfer.files[0];
      if (file && file.type === "application/pdf") {
        setFileName(file.name);
        onUpload(file);
      }
    },
    [onUpload]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setFileName(file.name);
        onUpload(file);
      }
    },
    [onUpload]
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`
        border-4 border-dashed border-primary p-12
        text-center cursor-pointer
        transition-all duration-100
        ${
          isDragOver
            ? "bg-accent translate-x-[2px] translate-y-[2px]"
            : "bg-surface hover:bg-accent"
        }
        ${isUploading ? "pointer-events-none opacity-70" : ""}
      `}
    >
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
        id="pdf-upload"
        disabled={isUploading}
      />
      <label htmlFor="pdf-upload" className="cursor-pointer block">
        {isUploading ? (
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-12 h-12 animate-spin" />
            <div>
              <p className="font-bold text-lg">Processing document...</p>
              <p className="text-text-secondary text-sm mt-1">
                {fileName || "Building document tree"}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <div className="bg-primary text-background p-4 border-2 border-primary shadow-brutal inline-block">
              {fileName ? (
                <FileText className="w-10 h-10" />
              ) : (
                <Upload className="w-10 h-10" />
              )}
            </div>
            <div>
              <p className="font-bold text-lg">
                {fileName || "PDF yahan drop karo"}
              </p>
              <p className="text-text-secondary text-sm mt-1">
                ya click karke file choose karo
              </p>
            </div>
            <div className="btn-brutal text-sm mt-2">Upload PDF</div>
          </div>
        )}
      </label>
    </div>
  );
}
