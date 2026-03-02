const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

/**
 * Upload a PDF file to the backend.
 * Returns the doc_id for subsequent API calls.
 */
export async function uploadPDF(file: File): Promise<{ doc_id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BACKEND_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.error || "Upload failed");
  }

  return response.json();
}

/**
 * Get the document tree (JSON + ASCII representation).
 */
export async function getTree(docId: string): Promise<{
  doc_id: string;
  tree: any;
  ascii: string;
}> {
  const response = await fetch(`${BACKEND_URL}/tree/${docId}`);

  if (!response.ok) {
    if (response.status === 202) {
      throw new Error("STILL_PROCESSING");
    }
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to get tree");
  }

  return response.json();
}

/**
 * Query the document via PageIndex + Gemini.
 */
export async function queryDocument(
  docId: string,
  query: string,
  nodeId?: string,
  language: string = "hi",
  inputMode: string = "text",
  outputMode: string = "text"
): Promise<{
  exact_quote: string;
  simple_explanation: string;
  source: { page: number; section: string; node_id: string };
  follow_up_suggestions: string[];
  audio_url?: string;
}> {
  const response = await fetch(`${BACKEND_URL}/query/${docId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      node_id: nodeId,
      language,
      input_mode: inputMode,
      output_mode: outputMode,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Query failed");
  }

  return response.json();
}

/**
 * Get the total page count for a document.
 */
export async function getPageCount(
  docId: string
): Promise<{ doc_id: string; page_count: number }> {
  const response = await fetch(`${BACKEND_URL}/page-count/${docId}`);

  if (!response.ok) {
    throw new Error("Failed to get page count");
  }

  return response.json();
}

/**
 * Get the URL for a specific PDF page image.
 */
export function getPageImageUrl(docId: string, pageNumber: number): string {
  return `${BACKEND_URL}/page/${docId}/${pageNumber}`;
}

/**
 * Connect to the WebSocket for real-time processing status updates.
 */
export function connectStatusWebSocket(
  docId: string,
  onMessage: (data: {
    status: string;
    progress: number;
    nodes_built: number;
    current_node: string | null;
    tree_ascii: string;
  }) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket {
  const wsUrl = BACKEND_URL.replace(/^http/, "ws");
  const ws = new WebSocket(`${wsUrl}/ws/status/${docId}`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      console.error("Failed to parse WebSocket message");
    }
  };

  ws.onerror = (error) => {
    onError?.(error);
  };

  ws.onclose = () => {
    onClose?.();
  };

  return ws;
}

/**
 * Get the backend URL (for direct image src usage etc.)
 */
export function getBackendUrl(): string {
  return BACKEND_URL;
}
