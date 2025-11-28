FROM node:18-alpine as builder

WORKDIR /app

ARG BACKEND_URL=http://backend_user:8000

COPY package.json package-lock.json ./

RUN npm install && npm cache clean --force

COPY . .

ENV NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL

# Build Next.js app
RUN npm run build

# Create public folder if it doesn't exist
RUN mkdir -p /app/public


FROM node:18-alpine as runtime

WORKDIR /app

ENV NODE_ENV=production

# Copy package files
COPY package.json package-lock.json ./

# Copy built Next.js app from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]
