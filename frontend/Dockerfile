FROM node:18-alpine as builder

WORKDIR /app

COPY package.json package-lock.json ./


RUN npm install && npm cache clean --force


COPY . .

RUN npm run build


FROM node:18-alpine as runtime

WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json


COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps --only=production && npm cache clean --force


RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]
