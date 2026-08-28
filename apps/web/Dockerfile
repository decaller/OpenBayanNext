# Build stage
FROM node:22-alpine AS builder
WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy root workspace files
COPY pnpm-lock.yaml* package.json pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

# Copy web source
COPY apps/web ./apps/web

# Build web
RUN pnpm --filter @openbayan/web build

# Production runtime stage
FROM node:22-alpine AS runner
WORKDIR /app
ENV HOST=0.0.0.0
ENV PORT=4321
EXPOSE 4321

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY --from=builder /app ./

CMD ["pnpm", "--filter", "@openbayan/web", "preview", "--host", "0.0.0.0", "--port", "4321"]
