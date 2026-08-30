# OpenBayan Production Deployment Guide

This guide covers deploying OpenBayan to production using **Portainer Stack (Git Repository)**, **Docker Compose CLI**, and configuring the **Zoraxy Reverse Proxy** for automated SSL and single-domain routing.

---

## 1. Portainer Git Stack Deployment (Recommended)

Portainer allows zero-downtime, continuous deployment directly from your GitHub repository.

### Step 1: Create a New Stack in Portainer
1. Open your Portainer Web UI (`https://your-portainer-ip:9443`).
2. Navigate to **Stacks** $\to$ **Add stack**.
3. Select **Repository** build method.
4. Fill in the repository details:
   - **Name**: `openbayan`
   - **Repository URL**: `https://github.com/decaller/OpenBayanNext`
   - **Repository Reference**: `refs/heads/main` (or target branch)
   - **Compose path**: `compose.yml`

### Step 2: Configure Environment Variables
In the **Environment variables** section, define:
```bash
DOMAIN=openbayan.mustaqbal.or.id
SITE_URL=https://openbayan.mustaqbal.or.id
WEB_PORT=4321
DATABASE_CDN_URL=https://huggingface.co/datasets/YourOrg/openbayan-data/resolve/main/shamela_corpus.db
```

### Step 3: Enable Auto-Update / Webhook
1. Enable **Automatic updates** (Polling or Webhook).
2. Copy the generated Webhook URL to configure GitHub Webhooks for automated builds on `git push`.
3. Click **Deploy the stack**.

---

## 2. Manual Docker Compose CLI Deployment

To deploy directly on a VPS or server via SSH:

```bash
# 1. Clone repository
git clone https://github.com/decaller/OpenBayanNext.git
cd OpenBayanNext

# 2. Copy and configure environment variables
cp .env.example .env
nano .env

# 3. If you have shamela_corpus.db locally, copy it into the data volume:
# docker volume create openbayan-data
# docker run --rm -v openbayan-data:/data -v $(pwd)/data:/src alpine cp /src/shamela_corpus.db /data/

# 4. Start the stack
docker compose up -d --build
```

---

## 3. Zoraxy Reverse Proxy Setup (Single Domain & SSL)

OpenBayan is designed to run behind **Zoraxy** on port 80/443 with zero CORS issues.

### Reverse Proxy Rule:
1. In Zoraxy dashboard, add a new **Proxy Rule**:
   - **Root Domain / Subdomain**: `openbayan.mustaqbal.or.id`
   - **Target IP / Host**: `127.0.0.1:4321` (or internal container `web:4321`)
   - **WebSocket Support**: `Enabled` (for live telemetry/drawers)
2. **TLS / SSL**:
   - Enable **Let's Encrypt ACME Certificate** for `openbayan.mustaqbal.or.id`.
   - Enable **Force HTTPS (HSTS)**.
3. **Caching Optimization**:
   - Set standard browser caching for `/_astro/*` (Immutable Vite assets) and `/p/*` (Classical Islamic text passages).

---

## 4. Verifying Crawlability & Search Bots

After deploying, run the automated crawler test suite against your live domain:

```bash
# Run multi-bot verification
bash scripts/benchmark_crawlers.sh https://openbayan.mustaqbal.or.id
```

### Expected Output:
- `✓ [PASS] Googlebot -> Status: 200 | Extracted: 'ScholarlyArticle'`
- `✓ [PASS] GPTBot -> Status: 200 | Extracted: 'السبكي'`
- `✓ [PASS] ClaudeBot -> Status: 200 | Extracted: 'data-copy-ai'`
- `✓ [PASS] PerplexityBot -> Status: 200 | Extracted: 'passage-card'`
- `✓ [PASS] Markdown Endpoint -> Status: 200 | Extracted: 'title:'`
- `✓ [PASS] OpenSearch Discovery -> Status: 200 | Extracted: 'OpenSearchDescription'`
- `✓ [PASS] LLMs.txt Protocol -> Status: 200 | Extracted: 'OpenBayan'`
- `✓ [PASS] Sitemap Index -> Status: 200 | Extracted: 'sitemapindex'`
