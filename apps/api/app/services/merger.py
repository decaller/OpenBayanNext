from typing import List, Dict, Any
from app.schemas.search import SearchResultItem

def merge_contiguous_siblings(
    items: List[SearchResultItem], 
    continuity_bonus: float = 1.05
) -> List[SearchResultItem]:
    """
    Fuses contiguous adjacent pages (chunk_order_{i+1} == chunk_order_i + 1)
    from the same book into a unified reading passage.
    
    Score formula:
        Score_merged = max(Score_A, Score_B) * 1.05
        
    Concatenates text with a clear page break delimiter and combines page labels,
    while preserving all author, category, tradition, and section start metadata.
    """
    if not items:
        return []

    merged: List[SearchResultItem] = []
    consumed = set()

    for i in range(len(items)):
        if i in consumed:
            continue
        
        current = items[i]
        merged_ids = [current.chunk_id]
        combined_text = current.full_text
        combined_footnotes = current.footnotes or ""
        vol_pages = [current.volume_page]
        max_rrf = current.rrf_score
        max_bm25 = current.bm25_score
        max_vec = current.vector_score
        is_merged = False

        # Look ahead for adjacent siblings
        for j in range(i + 1, len(items)):
            if j in consumed:
                continue
            candidate = items[j]
            
            # Check same book and consecutive chunk order
            if candidate.book_id == current.book_id:
                # Sibling directly following or preceding
                if abs(candidate.chunk_order - current.chunk_order) == 1:
                    consumed.add(j)
                    is_merged = True
                    merged_ids.append(candidate.chunk_id)
                    
                    # Merge in logical reading order (ascending chunk_order)
                    if candidate.chunk_order > current.chunk_order:
                        combined_text = f"{combined_text}\n\n<hr class=\"page-divider\"/>\n\n{candidate.full_text}"
                        vol_pages.append(candidate.volume_page)
                    else:
                        combined_text = f"{candidate.full_text}\n\n<hr class=\"page-divider\"/>\n\n{combined_text}"
                        vol_pages.insert(0, candidate.volume_page)

                    if candidate.footnotes:
                        if combined_footnotes:
                            combined_footnotes = f"{combined_footnotes}\n---\n{candidate.footnotes}"
                        else:
                            combined_footnotes = candidate.footnotes

                    # Scoring formula: max(A, B) * 1.05
                    max_rrf = max(max_rrf, candidate.rrf_score) * continuity_bonus
                    if candidate.bm25_score is not None:
                        max_bm25 = max(max_bm25 or 0.0, candidate.bm25_score)
                    if candidate.vector_score is not None:
                        max_vec = max(max_vec or 0.0, candidate.vector_score)

        # Build merged result item
        page_range_str = " - ".join(dict.fromkeys(vol_pages)) if len(vol_pages) > 1 else current.volume_page
        snippet = combined_text[:350].replace("\r", " ").replace("\n", " ") + ("..." if len(combined_text) > 350 else "")

        merged_item = SearchResultItem(
            chunk_id=current.chunk_id,
            book_id=current.book_id,
            book_name=current.book_name,
            author_name=current.author_name,
            author_death_hijri=current.author_death_hijri,
            category_name=current.category_name,
            author_tradition=current.author_tradition,
            era_tag=current.era_tag,
            volume_page=page_range_str,
            chunk_order=current.chunk_order,
            section_id=current.section_id,
            section_title=current.section_title,
            breadcrumb=current.breadcrumb,
            text_snippet=snippet,
            full_text=combined_text,
            footnotes=combined_footnotes if combined_footnotes else None,
            bm25_score=max_bm25,
            vector_score=max_vec,
            rrf_score=max_rrf,
            is_merged=is_merged,
            is_section_start=current.is_section_start,
            merged_chunk_ids=merged_ids if is_merged else [current.chunk_id],
            merged_page_range=page_range_str if is_merged else None
        )
        merged.append(merged_item)

    # Sort merged results by final RRF score descending
    merged.sort(key=lambda x: x.rrf_score, reverse=True)
    return merged
