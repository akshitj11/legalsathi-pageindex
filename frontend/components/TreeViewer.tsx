"use client";

import { useMemo } from "react";

export interface TreeNode {
  id: string;
  label: string;
  label_hi?: string;
  pages?: string;
  summary?: string;
  children?: TreeNode[];
}

interface TreeViewerProps {
  tree: TreeNode | null;
  asciiTree?: string;
  onNodeClick: (node: TreeNode) => void;
  isLoading?: boolean;
}

export default function TreeViewer({
  tree,
  asciiTree,
  onNodeClick,
  isLoading,
}: TreeViewerProps) {
  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header flex items-center justify-between">
        <span>Document Tree</span>
        {isLoading && (
          <span className="text-green-400 text-xs animate-pulse-brutal">
            Building...
          </span>
        )}
      </div>

      <div className="flex-1 overflow-auto">
        {asciiTree ? (
          <AsciiTreeView
            asciiTree={asciiTree}
            tree={tree}
            onNodeClick={onNodeClick}
          />
        ) : tree ? (
          <InteractiveTree node={tree} onNodeClick={onNodeClick} depth={0} />
        ) : (
          <div className="p-6 text-center text-text-secondary">
            <p className="font-mono text-sm">Waiting for document tree...</p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Renders the ASCII tree in a dark code block with clickable nodes.
 */
function AsciiTreeView({
  asciiTree,
  tree,
  onNodeClick,
}: {
  asciiTree: string;
  tree: TreeNode | null;
  onNodeClick: (node: TreeNode) => void;
}) {
  const flatNodes = useMemo(() => {
    if (!tree) return new Map<string, TreeNode>();
    const map = new Map<string, TreeNode>();
    flattenTree(tree, map);
    return map;
  }, [tree]);

  const lines = asciiTree.split("\n");

  return (
    <div className="tree-block min-h-full">
      <pre className="whitespace-pre font-mono text-xs leading-relaxed">
        {lines.map((line, i) => {
          // Try to match this line to a tree node
          const matchedNode = findNodeForLine(line, flatNodes);

          if (matchedNode) {
            return (
              <div
                key={i}
                className="tree-node px-1 -mx-1 hover:bg-white/10 cursor-pointer"
                onClick={() => onNodeClick(matchedNode)}
                title={`Click: "${matchedNode.label_hi || matchedNode.label}" ke baare mein batao`}
              >
                {line}
              </div>
            );
          }

          return (
            <div key={i} className="px-1 -mx-1">
              {line}
            </div>
          );
        })}
      </pre>
    </div>
  );
}

/**
 * Interactive tree renderer (used when ASCII tree is not available).
 * Renders nodes as clickable indented items.
 */
function InteractiveTree({
  node,
  onNodeClick,
  depth,
  isLast = true,
}: {
  node: TreeNode;
  onNodeClick: (node: TreeNode) => void;
  depth: number;
  isLast?: boolean;
}) {
  const label = node.label_hi || node.label;
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className={depth === 0 ? "tree-block min-h-full" : ""}>
      <div
        className="tree-node px-1 -mx-1 hover:bg-white/10 cursor-pointer font-mono text-xs"
        onClick={() => onNodeClick(node)}
        style={{ paddingLeft: `${depth * 24}px` }}
      >
        <span className="text-gray-500">
          {depth > 0 ? (isLast ? "└── " : "├── ") : ""}
        </span>
        <span className="text-green-400">{label}</span>
        {node.pages && (
          <span className="text-gray-500"> (pages {node.pages})</span>
        )}
      </div>

      {node.summary && hasChildren && (
        <div
          className="font-mono text-xs text-yellow-300/70"
          style={{ paddingLeft: `${(depth + 1) * 24}px` }}
        >
          {depth > 0 ? "├── " : ""}summary: &quot;{node.summary.slice(0, 60)}
          {node.summary.length > 60 ? "..." : ""}&quot;
        </div>
      )}

      {node.children?.map((child, i) => (
        <InteractiveTree
          key={child.id}
          node={child}
          onNodeClick={onNodeClick}
          depth={depth + 1}
          isLast={i === node.children!.length - 1}
        />
      ))}
    </div>
  );
}

/** Flatten tree into a Map<label, TreeNode> for line matching */
function flattenTree(node: TreeNode, map: Map<string, TreeNode>) {
  map.set(node.label, node);
  if (node.label_hi) {
    map.set(node.label_hi, node);
  }
  node.children?.forEach((child) => flattenTree(child, map));
}

/** Try to find a matching tree node for an ASCII tree line */
function findNodeForLine(
  line: string,
  flatNodes: Map<string, TreeNode>
): TreeNode | null {
  // Strip tree drawing characters to get the label
  const cleaned = line.replace(/[│├└─\s]/g, "").split("(pages")[0].trim();

  // Also try with summary prefix removed
  if (cleaned.startsWith('summary:"')) return null;

  let found: TreeNode | null = null;
  flatNodes.forEach((node, key) => {
    if (!found && cleaned === key.replace(/\s/g, "")) {
      found = node;
    }
  });
  return found;

  return null;
}
