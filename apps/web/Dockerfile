# Multi-Stage Lean Node Container for OpenBayan Astro SSR Web
FROM node:22-alpine AS builder

WORKDIR /app

# Enable corepack and stable pnpm
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

# Copy app dependencies manifests
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy application source code
COPY . .

# Build Astro standalone SSR bundle
RUN pnpm run build

# Final Production Image
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=4321

# Copy build artifacts and dependencies from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

# Create non-root user
USER node

EXPOSE 4321

# Healthcheck
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --spider -q http://localhost:4321/ || exit 1

CMD ["node", "dist/server/entry.mjs"]
