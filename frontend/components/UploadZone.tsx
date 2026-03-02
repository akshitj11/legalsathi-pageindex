"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, Image, FileType, Loader2 } from "lucide-react";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export default function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const ACCEPTED_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ];

  const ACCEPTED_EXTENSIONS = ".pdf,.jpg,.jpeg,.png,.webp,.bmp,.txt,.doc,.docx";

  const isAcceptedFile = (file: File): boolean => {
    if (ACCEPTED_TYPES.indexOf(file.type) !== -1) return true;
    // Fallback: check extension
    const ext = file.name.toLowerCase().split(".").pop() || "";
    const validExts = ["pdf", "jpg", "jpeg", "png", "webp", "bmp", "txt", "doc", "docx"];
    return validExts.indexOf(ext) !== -1;
  };

  const getFileIcon = () => {
    if (!fileName) return <Upload className="w-10 h-10" />;
    const ext = fileName.toLowerCase().split(".").pop() || "";
    if (["jpg", "jpeg", "png", "webp", "bmp"].indexOf(ext) !== -1) {
      return <Image className="w-10 h-10" />;
    }
    if (["txt", "doc", "docx"].indexOf(ext) !== -1) {
      return <FileType className="w-10 h-10" />;
    }
    return <FileText className="w-10 h-10" />;
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const file = e.dataTransfer.files[0];
      if (file && isAcceptedFile(file)) {
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
        accept={ACCEPTED_EXTENSIONS}
        onChange={handleFileSelect}
        className="hidden"
        id="file-upload"
        disabled={isUploading}
      />
      <label htmlFor="file-upload" className="cursor-pointer block">
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
              {getFileIcon()}
            </div>
            <div>
              <p className="font-bold text-lg">
                {fileName || "Document yahan drop karo"}
              </p>
              <p className="text-text-secondary text-sm mt-1">
                PDF, Image (JPG/PNG), ya Text file (TXT/DOCX)
              </p>
            </div>
            <div className="btn-brutal text-sm mt-2">Upload Document</div>
          </div>
        )}
      </label>
    </div>
  );
}
