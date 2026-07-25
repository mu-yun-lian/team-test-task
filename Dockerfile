# syntax=docker/dockerfile:1.7

# ---------- Stage 1: build the React client ----------
FROM node:18-alpine AS client-build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install --no-audit --no-fund
COPY client/ ./
RUN npm run build

# ---------- Stage 2: install server production deps ----------
FROM node:18-alpine AS server-deps
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev --no-audit --no-fund

# ---------- Stage 3: final runtime image ----------
FROM node:18-alpine AS runtime
WORKDIR /app

# curl is handy for `docker exec ... curl` checks; tzdata keeps logs in local time
RUN apk add --no-cache curl tzdata

ENV NODE_ENV=production \
    PORT=8080

COPY --from=server-deps /app/node_modules ./node_modules
COPY . .
COPY --from=client-build /app/client/build ./client/build

EXPOSE 8080

# Lightweight container healthcheck hitting the express health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8080/health || exit 1

CMD ["node", "server.js"]
