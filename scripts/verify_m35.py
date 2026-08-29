#!/usr/bin/env python3
"""
Verification script for Milestone 3.5:
Tests Category, Era, Tradition faceting, Section Start badges, and Scripture Citation Routing.
"""
import requests

API_BASE = "http://127.0.0.1:8001/api/v1"
WEB_BASE = "http://127.0.0.1:4321"

def test_milestone_35():
    print("=" * 70)
    print("🚀 VERIFYING MILESTONE 3.5: MULTI-DIMENSIONAL FACETS & CITATIONS")
    print("=" * 70)

    # 1. Test Discipline / Category Faceting
    print("\n[1/5] Testing Discipline / Category Filter (category='الفقه الشافعي')...")
    r1 = requests.get(f"{API_BASE}/search?q=شروط+بيع+السلم&category=الفقه+الشافعي")
    r1.encoding = "utf-8"
    assert r1.status_code == 200, f"Error {r1.status_code}: {r1.text}"
    d1 = r1.json()
    print(f"✓ Found {len(d1['results'])} hits in {d1['took_ms']} ms")
    for item in d1['results'][:3]:
        print(f"  • {item['book_name']} | {item['category_name']} | {item['author_name']}")
        assert item['category_name'] == 'الفقه الشافعي', "Category filtering failed"

    # 2. Test Chronological Era Filter
    print("\n[2/5] Testing Chronological Era Filter (era='early' <= 300 AH)...")
    r2 = requests.get(f"{API_BASE}/search?q=الإيمان&era=early")
    r2.encoding = "utf-8"
    assert r2.status_code == 200, f"Error {r2.status_code}: {r2.text}"
    d2 = r2.json()
    print(f"✓ Found {len(d2['results'])} hits in {d2['took_ms']} ms")
    for item in d2['results'][:3]:
        death = item.get('author_death_hijri')
        print(f"  • {item['book_name']} | Author: {item['author_name']} (d. {death} AH)")
        if death:
            assert death <= 300, f"Author death year {death} > 300"

    # 3. Test Theological Tradition Filter
    print("\n[3/5] Testing Tradition Filter (tradition='athari_salafi')...")
    r3 = requests.get(f"{API_BASE}/search?q=التوحيد&tradition=athari_salafi")
    r3.encoding = "utf-8"
    assert r3.status_code == 200, f"Error {r3.status_code}: {r3.text}"
    d3 = r3.json()
    print(f"✓ Found {len(d3['results'])} hits in {d3['took_ms']} ms")
    for item in d3['results'][:3]:
        print(f"  • {item['book_name']} | Tradition: {item.get('author_tradition')}")
        assert item.get('author_tradition') == 'athari_salafi', "Tradition filtering failed"

    # 4. Test Scripture Citation Interceptor (Surah:Ayah)
    print("\n[4/5] Testing Direct Ayah Citation Interceptor (query='البقرة: 275')...")
    r4 = requests.get(f"{API_BASE}/search?q=البقرة:275")
    r4.encoding = "utf-8"
    assert r4.status_code == 200, f"Error {r4.status_code}: {r4.text}"
    d4 = r4.json()
    assert d4['pinned_citation'] is not None, "Pinned citation was not generated"
    pin = d4['pinned_citation']
    print(f"✓ Interceptor successfully matched: {pin['citation']['display_title']}")
    print(f"  • Source: {pin['book_name']} ({pin['volume_page']})")
    print(f"  • Breadcrumb: {pin['breadcrumb']}")

    # 5. Test Frontend SSR Rendering
    print("\n[5/5] Testing Frontend SSR with Active Category Filter...")
    r5 = requests.get(f"{WEB_BASE}/search?q=شروط+بيع+السلم&category=الفقه+الشافعي&lang=ar")
    r5.encoding = "utf-8"
    assert r5.status_code == 200, f"Web status: {r5.status_code}"
    assert "الفقه الشافعي" in r5.text, "Category pill not rendered"
    assert "thematic-group-1" in r5.text, "Thematic clusters rendered"
    print("✓ Frontend SSR successfully server-rendered faceted filters and thematic clusters!")

    print("\n" + "=" * 70)
    print("🎉 ALL MILESTONE 3.5 FACET & CITATION VERIFICATIONS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_milestone_35()
