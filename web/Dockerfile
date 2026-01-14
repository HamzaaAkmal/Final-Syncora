# Dockerfile for Syncora frontend (Next.js dev setup)
# For hackathon/demo purposes we run Next in dev mode. For production, build and use a lighter server.
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY web/package*.json ./
RUN npm ci --silent

# Copy source
COPY web/ ./

# Expose dev port
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_BASE=http://backend:8001
EXPOSE 3782

CMD ["npm", "run", "dev"]
