# Cura3.ai Frontend — Dockerfile
FROM node:22-alpine AS builder

WORKDIR /app

# Dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Build args for env
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Application code
COPY . .

# Build
RUN npm run build

# ── Production Stage ─────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built output
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --spider --quiet http://localhost:3000 || exit 1

CMD ["npm", "start"]
