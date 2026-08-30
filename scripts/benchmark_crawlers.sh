#!/usr/bin/env bash
set -eo pipefail

HOST="${1:-http://localhost:4321}"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================================================"
echo -e "${BLUE}🤖 BENCHMARKING SEARCH BOTS, CRAWLERS & PROTOCOLS ON: $HOST${NC}"
echo "======================================================================"

test_bot() {
  local name="$1"
  local ua="$2"
  local url="$3"
  local expect_string="$4"

  local tmp_body
  tmp_body=$(mktemp)
  
  local http_code
  local ttfb

  http_code=$(curl -s -L -A "$ua" -w "%{http_code}" -o "$tmp_body" "$url" || echo "500")
  ttfb=$(curl -s -L -A "$ua" -o /dev/null -w "%{time_starttransfer}" "$url" || echo "0")

  if [ "$http_code" -eq 200 ] && grep -q "$expect_string" "$tmp_body"; then
    echo -e "✓ [${GREEN}PASS${NC}] $name -> Status: $http_code | TTFB: ${ttfb}s | Extracted: '$expect_string'"
    rm -f "$tmp_body"
  else
    echo -e "❌ [${RED}FAIL${NC}] $name -> Status: $http_code | Target missing: '$expect_string'"
    rm -f "$tmp_body"
    return 1
  fi
}

echo -e "\n1. Testing 0-JS HTML Permalink (/p/1):"
test_bot "Googlebot (Schema.org)" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "$HOST/p/1" "ScholarlyArticle"
test_bot "Googlebot (Breadcrumbs)" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "$HOST/p/1" "BreadcrumbList"
test_bot "GPTBot (Arabic Matn)" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)" "$HOST/p/1" "الحمد لله"
test_bot "ClaudeBot (AI Hooks)" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +https://www.anthropic.com/claudebot)" "$HOST/p/1" "data-copy-ai"

echo -e "\n2. Testing Pure Markdown Agent Route (/p/1.md):"
test_bot "Markdown Route (YAML)" "curl/8.0" "$HOST/p/1.md" "title:"
test_bot "Markdown Route (Permalink)" "curl/8.0" "$HOST/p/1.md" "permalink:"

echo -e "\n3. Testing SSR Search Page (/search?q=النية):"
test_bot "PerplexityBot (Search Cards)" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0)" "$HOST/search?q=%D8%A7%D9%84%D9%86%D9%8A%D8%A9" "passage-card"

echo -e "\n4. Testing Machine-Readable Discovery Protocols:"
test_bot "OpenSearch Discovery" "curl/8.0" "$HOST/opensearch.xml" "OpenSearchDescription"
test_bot "LLMs.txt Protocol" "curl/8.0" "$HOST/llms.txt" "OpenBayan"
test_bot "LLMs-full.txt Catalog" "curl/8.0" "$HOST/llms-full.txt" "صحيح البخاري"
test_bot "Robots Policy" "curl/8.0" "$HOST/robots.txt" "GPTBot"

echo -e "\n5. Testing Scalable Sitemap Index & Partitions:"
test_bot "Sitemap Index" "curl/8.0" "$HOST/sitemap.xml" "sitemapindex"
test_bot "Sitemap Core" "curl/8.0" "$HOST/sitemaps/core.xml" "urlset"
test_bot "Sitemap Books" "curl/8.0" "$HOST/sitemaps/books.xml" "urlset"
test_bot "Sitemap Chunks Part 1" "curl/8.0" "$HOST/sitemaps/chunks-1.xml" "urlset"

echo -e "\n======================================================================"
echo -e "${GREEN}🎉 ALL 14 CRAWLER AND DISCOVERY BENCHMARKS PASSED PERFECTLY!${NC}"
echo "======================================================================"
