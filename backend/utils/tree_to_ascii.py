"""
Tree-to-ASCII utility - Converts PageIndex JSON tree to ASCII markdown string.

Produces output like:
Rent Agreement
├── Paise se Related (pages 1-5)
│   ├── summary: "Tenant shall pay ₹8,000 by 5th..."
│   ├── Kiraya Kitna Dena Hai (pages 1-2)
│   └── Late Payment Rules (pages 2-3)
├── Ghar se Related (pages 6-10)
│   ├── Lock-in Period (pages 6-7)
│   └── Occupancy Rules (pages 8-9)
└── Zaruri Baatein (pages 11-15)
    ├── Deposit Wapsi (pages 11-12)
    └── Termination Rules (pages 13-15)
"""


def tree_to_ascii(node: dict, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
    """
    Recursively convert a tree node dictionary to an ASCII tree string.

    Args:
        node: Tree node dict with keys: label/label_hi, pages, children, summary
        prefix: Current line prefix for indentation
        is_last: Whether this node is the last child
        is_root: Whether this is the root node

    Returns:
        ASCII tree string
    """
    lines = []

    # Determine the display label (prefer Hindi label)
    label = node.get("label_hi") or node.get("label", "Unknown")
    pages = node.get("pages", "")
    node_id = node.get("id", "")

    # Build the node line
    if is_root:
        # Root node — no connector
        page_suffix = f" (pages {pages})" if pages else ""
        lines.append(f"{label}{page_suffix}")
        child_prefix = ""
    else:
        connector = "└── " if is_last else "├── "
        page_suffix = f" (pages {pages})" if pages else ""
        lines.append(f"{prefix}{connector}{label}{page_suffix}")
        child_prefix = prefix + ("    " if is_last else "│   ")

    # Add summary if present
    summary = node.get("summary", "")
    if summary and not is_root:
        summary_connector = "│   " if not is_last else "    "
        truncated = summary[:60] + "..." if len(summary) > 60 else summary
        # Only show summary for nodes with children
        if node.get("children"):
            lines.append(f'{child_prefix}├── summary: "{truncated}"')

    # Render children
    children = node.get("children", [])
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        child_ascii = tree_to_ascii(
            child,
            prefix=child_prefix,
            is_last=is_last_child,
            is_root=False,
        )
        lines.append(child_ascii)

    return "\n".join(lines)


def json_tree_to_flat_nodes(node: dict, parent_id: str = None) -> list:
    """
    Flatten a tree into a list of nodes with parent references.
    Useful for search and lookup operations.

    Args:
        node: Tree node dictionary
        parent_id: ID of the parent node

    Returns:
        List of flat node dicts with parent_id references
    """
    flat = []
    node_id = node.get("id", "root")

    flat.append({
        "id": node_id,
        "label": node.get("label", ""),
        "label_hi": node.get("label_hi", ""),
        "pages": node.get("pages", ""),
        "summary": node.get("summary", ""),
        "parent_id": parent_id,
    })

    for child in node.get("children", []):
        flat.extend(json_tree_to_flat_nodes(child, parent_id=node_id))

    return flat


def find_node_by_id(node: dict, target_id: str) -> dict | None:
    """
    Find a node in the tree by its ID.

    Args:
        node: Root tree node
        target_id: ID to search for

    Returns:
        The matching node dict, or None
    """
    if node.get("id") == target_id:
        return node

    for child in node.get("children", []):
        result = find_node_by_id(child, target_id)
        if result:
            return result

    return None
