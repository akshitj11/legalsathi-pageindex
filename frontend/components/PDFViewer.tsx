"use client";

import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, FileText, Image } from "lucide-react";

interface PDFViewerProps {
  docId: string;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  backendUrl: string;
  fileType?: string; // "pdf" | "image" | "text"
}

export default function PDFViewer({
  docId,
  currentPage,
  totalPages,
  onPageChange,
  backendUrl,
  fileType = "pdf",
}: PDFViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [textContent, setTextContent] = useState<string | null>(null);

  const imageUrl = `${backendUrl}/page/${docId}/${currentPage}`;

  useEffect(() => {
    setIsLoading(true);

    // For text files, fetch the text content as JSON
    if (fileType === "text") {
      fetch(imageUrl)
        .then((res) => res.json())
        .then((data) => {
          setTextContent(data.text || "");
          setIsLoading(false);
        })
        .catch(() => {
          setTextContent("[Could not load text content]");
          setIsLoading(false);
        });
    }
  }, [currentPage, fileType, imageUrl]);

  const handlePrevPage = () => {
    if (currentPage > 1) onPageChange(currentPage - 1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) onPageChange(currentPage + 1);
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.25, 0.5));
  };

  const headerLabel =
    fileType === "image"
      ? "Image Viewer"
      : fileType === "text"
      ? "Document Viewer"
      : "PDF Viewer";

  return (
    <div className="panel flex flex-col h-full">
      {/* Header with controls */}
      <div className="panel-header flex items-center justify-between">
        <div className="flex items-center gap-2">
          {fileType === "image" ? (
            <Image className="w-4 h-4" />
          ) : fileType === "text" ? (
            <FileText className="w-4 h-4" />
          ) : null}
          <span>{headerLabel}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-1 hover:bg-white/20 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs">{Math.round(zoom * 100)}%</span>
          <button
            onClick={handleZoomIn}
            className="p-1 hover:bg-white/20 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto bg-gray-100 flex items-start justify-center p-4">
        {fileType === "text" ? (
          /* Text Document Viewer */
          isLoading ? (
            <div className="w-full max-w-[595px] bg-white border-2 border-primary shadow-brutal p-8 flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-primary border-t-transparent animate-spin mx-auto mb-2" />
                <p className="text-text-secondary text-sm">Loading document...</p>
              </div>
            </div>
          ) : (
            <div
              style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
              className="transition-transform duration-200 w-full max-w-[595px]"
            >
              <div className="bg-white border-2 border-primary shadow-brutal p-8">
                <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-primary break-words">
                  {textContent || "No content available"}
                </pre>
              </div>
            </div>
          )
        ) : totalPages > 0 ? (
          /* PDF / Image Viewer */
          <div
            style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
            className="transition-transform duration-200"
          >
            {isLoading && (
              <div className="w-[595px] h-[842px] bg-white border-2 border-primary shadow-brutal flex items-center justify-center">
                <div className="text-center">
                  <div className="w-8 h-8 border-4 border-primary border-t-transparent animate-spin mx-auto mb-2" />
                  <p className="text-text-secondary text-sm">
                    {fileType === "image" ? "Loading image..." : "Loading page..."}
                  </p>
                </div>
              </div>
            )}
            <img
              src={imageUrl}
              alt={fileType === "image" ? "Document Image" : `Page ${currentPage}`}
              className={`border-2 border-primary shadow-brutal max-w-none ${isLoading ? "hidden" : "block"}`}
              onLoad={() => setIsLoading(false)}
              onError={() => setIsLoading(false)}
              style={{ width: "595px" }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-text-secondary">
            <p className="font-mono text-sm">No content loaded</p>
          </div>
        )}
      </div>

      {/* Page Navigation - only show for multi-page PDFs */}
      {fileType === "pdf" && (
        <div className="border-t-2 border-primary bg-surface px-4 py-2 flex items-center justify-between">
          <button
            onClick={handlePrevPage}
            disabled={currentPage <= 1}
            className="btn-brutal-outline text-xs py-1 px-3 disabled:opacity-30 disabled:pointer-events-none"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-2">
            <span className="font-bold text-sm">
              Page {currentPage}
            </span>
            <span className="text-text-secondary text-sm">
              of {totalPages}
            </span>
          </div>

          <button
            onClick={handleNextPage}
            disabled={currentPage >= totalPages}
            className="btn-brutal-outline text-xs py-1 px-3 disabled:opacity-30 disabled:pointer-events-none"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Single-page indicator for images/text */}
      {fileType !== "pdf" && (
        <div className="border-t-2 border-primary bg-surface px-4 py-2 flex items-center justify-center">
          <span className="text-text-secondary text-xs font-mono">
            {fileType === "image" ? "Single Image Document" : "Text Document"}
          </span>
        </div>
      )}
    </div>
  );
}
