"use client";

import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from "lucide-react";

interface PDFViewerProps {
  docId: string;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  backendUrl: string;
}

export default function PDFViewer({
  docId,
  currentPage,
  totalPages,
  onPageChange,
  backendUrl,
}: PDFViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const imageUrl = `${backendUrl}/page/${docId}/${currentPage}`;

  useEffect(() => {
    setIsLoading(true);
  }, [currentPage]);

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

  return (
    <div className="panel flex flex-col h-full">
      {/* Header with controls */}
      <div className="panel-header flex items-center justify-between">
        <span>PDF Viewer</span>
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

      {/* PDF Page Image */}
      <div className="flex-1 overflow-auto bg-gray-100 flex items-start justify-center p-4">
        {totalPages > 0 ? (
          <div
            style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
            className="transition-transform duration-200"
          >
            {isLoading && (
              <div className="w-[595px] h-[842px] bg-white border-2 border-primary shadow-brutal flex items-center justify-center">
                <div className="text-center">
                  <div className="w-8 h-8 border-4 border-primary border-t-transparent animate-spin mx-auto mb-2" />
                  <p className="text-text-secondary text-sm">Loading page...</p>
                </div>
              </div>
            )}
            <img
              src={imageUrl}
              alt={`Page ${currentPage}`}
              className={`border-2 border-primary shadow-brutal max-w-none ${isLoading ? "hidden" : "block"}`}
              onLoad={() => setIsLoading(false)}
              onError={() => setIsLoading(false)}
              style={{ width: "595px" }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-text-secondary">
            <p className="font-mono text-sm">No pages loaded</p>
          </div>
        )}
      </div>

      {/* Page Navigation */}
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
    </div>
  );
}
