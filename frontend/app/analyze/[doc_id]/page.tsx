"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { FileText, ArrowLeft, Loader2 } from "lucide-react";
import TreeViewer, { TreeNode } from "@/components/TreeViewer";
import PDFViewer from "@/components/PDFViewer";
import ChatPanel from "@/components/ChatPanel";
import {
  connectStatusWebSocket,
  getTree,
  getPageCount,
  queryDocument,
  getBackendUrl,
} from "@/lib/api";

export default function AnalyzePage() {
  const params = useParams();
  const router = useRouter();
  const docId = params.doc_id as string;

  // State
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [asciiTree, setAsciiTree] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [prefillQuery, setPrefillQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(true);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("Connecting...");

  // Connect WebSocket for real-time processing status
  useEffect(() => {
    if (!docId) return;

    const ws = connectStatusWebSocket(
      docId,
      (data) => {
        setProgress(data.progress);
        setStatusText(data.current_node || "Processing...");

        if (data.tree_ascii) {
          setAsciiTree(data.tree_ascii);
        }

        if (data.status === "completed") {
          setIsProcessing(false);
          // Fetch the full tree
          fetchTree();
          fetchPageCount();
        } else if (data.status === "error") {
          setIsProcessing(false);
          setStatusText("Error processing document");
        }
      },
      () => {
        // On WebSocket error, try polling instead
        pollForTree();
      },
      () => {
        // On close, if still processing, try polling
        if (isProcessing) {
          pollForTree();
        }
      }
    );

    return () => {
      ws.close();
    };
  }, [docId]);

  const fetchTree = useCallback(async () => {
    try {
      const data = await getTree(docId);
      setTree(data.tree);
      setAsciiTree(data.ascii);
    } catch {
      // Tree may not be ready yet
    }
  }, [docId]);

  const fetchPageCount = useCallback(async () => {
    try {
      const data = await getPageCount(docId);
      setTotalPages(data.page_count);
    } catch {
      setTotalPages(15); // Fallback for demo
    }
  }, [docId]);

  // Polling fallback if WebSocket fails
  const pollForTree = useCallback(async () => {
    const maxAttempts = 30;
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise((r) => setTimeout(r, 2000));
      try {
        const data = await getTree(docId);
        setTree(data.tree);
        setAsciiTree(data.ascii);
        setIsProcessing(false);
        fetchPageCount();
        return;
      } catch (err) {
        if (err instanceof Error && err.message !== "STILL_PROCESSING") {
          break;
        }
        setProgress(Math.min(90, (i + 1) * 3));
      }
    }
  }, [docId, fetchPageCount]);

  // Handle tree node click
  const handleNodeClick = (node: TreeNode) => {
    // Jump PDF to the first page of this node's range
    if (node.pages) {
      const firstPage = parseInt(node.pages.split("-")[0], 10);
      if (!isNaN(firstPage)) {
        setCurrentPage(firstPage);
      }
    }

    // Pre-fill chat with a question about this section
    const label = node.label_hi || node.label;
    setPrefillQuery(`"${label}" ke baare mein batao`);
  };

  // Handle query
  const handleQuery = async (
    query: string,
    language: string,
    inputMode: string,
    outputMode: string
  ) => {
    return queryDocument(docId, query, undefined, language, inputMode, outputMode);
  };

  // Handle source click from chat (jump to page)
  const handleSourceClick = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Bar */}
      <header className="border-b-4 border-primary bg-surface flex-shrink-0">
        <div className="px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/")}
              className="btn-brutal-outline py-1 px-2 text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2">
              <div className="bg-primary text-background p-1.5 border-2 border-primary shadow-brutal-sm">
                <FileText className="w-4 h-4" />
              </div>
              <span className="font-bold">LegalSaathi</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-text-secondary text-xs font-mono">
              Doc: {docId}
            </span>
            {isProcessing && (
              <div className="flex items-center gap-2 text-text-secondary text-xs">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>{progress}%</span>
              </div>
            )}
          </div>
        </div>

        {/* Progress bar */}
        {isProcessing && (
          <div className="h-1 bg-accent">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </header>

      {/* Processing overlay */}
      {isProcessing && !asciiTree && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent animate-spin mx-auto mb-6" />
            <h2 className="text-2xl font-bold mb-2">Document Process Ho Raha Hai</h2>
            <p className="text-text-secondary mb-4">{statusText}</p>
            <div className="w-64 h-3 bg-accent border-2 border-primary mx-auto">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-text-secondary text-sm mt-2">{progress}% complete</p>
          </div>
        </div>
      )}

      {/* Main 3-Panel Layout */}
      {(!isProcessing || asciiTree) && (
        <div className="flex-1 flex overflow-hidden">
          {/* LEFT: Tree Viewer */}
          <div className="w-1/4 min-w-[280px] border-r-2 border-primary flex-shrink-0">
            <TreeViewer
              tree={tree}
              asciiTree={asciiTree}
              onNodeClick={handleNodeClick}
              isLoading={isProcessing}
            />
          </div>

          {/* CENTER: PDF Viewer */}
          <div className="flex-1 min-w-[400px]">
            <PDFViewer
              docId={docId}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              backendUrl={getBackendUrl()}
            />
          </div>

          {/* RIGHT: Chat Panel */}
          <div className="w-1/4 min-w-[300px] border-l-2 border-primary flex-shrink-0">
            <ChatPanel
              docId={docId}
              onQuery={handleQuery}
              onSourceClick={handleSourceClick}
              prefillQuery={prefillQuery}
            />
          </div>
        </div>
      )}
    </div>
  );
}
