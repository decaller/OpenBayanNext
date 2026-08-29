import json
import os
from typing import Dict, List, Optional, Tuple, Any

class TOCNode:
    def __init__(self, title_id: int, book_id: int, page_id: int, parent_id: Optional[int], title_text: str):
        self.title_id = title_id
        self.book_id = book_id
        self.page_id = page_id
        self.parent_id = parent_id
        self.title_text = title_text.strip()
        self.children: List['TOCNode'] = []
        self.level: int = 1
        self.breadcrumb: str = ""
        self.start_page_id: int = page_id
        self.end_page_id: int = 999999999

class TOCResolver:
    def __init__(self, book_id: int, book_title: str, toc_path: Optional[str] = None):
        self.book_id = book_id
        self.book_title = book_title
        self.nodes_by_id: Dict[int, TOCNode] = {}
        self.nodes_by_page: Dict[int, List[TOCNode]] = {}
        self.sorted_entries: List[TOCNode] = []
        self.has_toc = False
        
        if toc_path and os.path.exists(toc_path):
            self._load_toc(toc_path)

    def _load_toc(self, toc_path: str):
        raw_entries = []
        with open(toc_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    title_id = data.get("title_id") or data.get("id")
                    page_id = data.get("page_id")
                    parent_id = data.get("parent_id")
                    title_text = data.get("title_text") or data.get("title") or ""
                    if title_id is not None and page_id is not None:
                        node = TOCNode(title_id, self.book_id, page_id, parent_id, title_text)
                        self.nodes_by_id[title_id] = node
                        if page_id not in self.nodes_by_page:
                            self.nodes_by_page[page_id] = []
                        self.nodes_by_page[page_id].append(node)
                        raw_entries.append(node)
                except Exception:
                    continue

        if not raw_entries:
            return

        self.has_toc = True
        
        # Build tree parent-child links
        root_nodes = []
        for node in raw_entries:
            if node.parent_id and node.parent_id in self.nodes_by_id:
                parent = self.nodes_by_id[node.parent_id]
                parent.children.append(node)
            else:
                root_nodes.append(node)

        # Depth-First Traversal to assign level and pre-computed breadcrumbs
        def dfs(curr_node: TOCNode, current_level: int, parent_breadcrumb: str):
            curr_node.level = current_level
            if parent_breadcrumb:
                curr_node.breadcrumb = f"{parent_breadcrumb} > {curr_node.title_text}"
            else:
                curr_node.breadcrumb = curr_node.title_text
                
            for child in curr_node.children:
                dfs(child, current_level + 1, curr_node.breadcrumb)

        for root in root_nodes:
            dfs(root, 1, self.book_title)

        # Sort all entries by page_id to create interval timeline
        self.sorted_entries = sorted(raw_entries, key=lambda n: (n.page_id, -n.level))

    def resolve_page(self, page_id: int) -> Tuple[str, int, str, str, bool]:
        """
        Resolves the active section metadata for a given page_id.
        Returns:
            (section_id, section_level, section_title, breadcrumb, is_section_start)
        """
        # 1. Fallback if no TOC exists
        if not self.has_toc or not self.sorted_entries:
            return (
                f"sec_{self.book_id}_main",
                1,
                self.book_title,
                self.book_title,
                False
            )

        # 2. Check if this page is an explicit section start
        is_section_start = page_id in self.nodes_by_page
        
        # If multiple headings on same page, pick the deepest / most granular level
        if is_section_start:
            matching_nodes = self.nodes_by_page[page_id]
            best_node = max(matching_nodes, key=lambda n: n.level)
            return (
                f"sec_{self.book_id}_{best_node.title_id}",
                best_node.level,
                best_node.title_text,
                best_node.breadcrumb,
                True
            )

        # 3. Pre-TOC Front Matter (page before first TOC entry)
        first_toc_page = self.sorted_entries[0].page_id
        if page_id < first_toc_page:
            return (
                f"sec_{self.book_id}_intro",
                1,
                "مقدمة الكتاب",
                f"{self.book_title} > مقدمة الكتاب",
                False
            )

        # 4. Binary search / linear scan for enclosing interval
        active_node = self.sorted_entries[0]
        for entry in self.sorted_entries:
            if entry.page_id <= page_id:
                active_node = entry
            else:
                break

        return (
            f"sec_{self.book_id}_{active_node.title_id}",
            active_node.level,
            active_node.title_text,
            active_node.breadcrumb,
            False
        )

    def get_all_sections_for_db(self) -> List[Dict[str, Any]]:
        """Returns all section records ready for insertion into the `sections` table."""
        records = []
        if not self.has_toc:
            records.append({
                "section_id": f"sec_{self.book_id}_main",
                "book_id": self.book_id,
                "parent_id": None,
                "title_text": self.book_title,
                "section_level": 1,
                "start_page_id": 1,
                "breadcrumb": self.book_title
            })
            return records

        for node in self.sorted_entries:
            records.append({
                "section_id": f"sec_{self.book_id}_{node.title_id}",
                "book_id": self.book_id,
                "parent_id": f"sec_{self.book_id}_{node.parent_id}" if node.parent_id else None,
                "title_text": node.title_text,
                "section_level": node.level,
                "start_page_id": node.page_id,
                "breadcrumb": node.breadcrumb
            })
        return records
