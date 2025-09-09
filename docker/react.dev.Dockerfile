# Development Dockerfile for React with hot-reload - using stable LTS version
FROM node:lts-alpine

# Install additional tools for development
RUN apk add --no-cache \
    curl \
    git \
    bash

# Set working directory
WORKDIR /app

# Copy package files
COPY src/react-frontend/package*.json ./

# Install all dependencies (including devDependencies)
# Using --legacy-peer-deps to handle TypeScript version conflicts with react-scripts
RUN npm ci --legacy-peer-deps

# Create non-root user (handle existing group gracefully)
RUN addgroup -g 1000 -S appuser 2>/dev/null || addgroup -S appuser && \
    adduser -u 1000 -S appuser -G appuser 2>/dev/null || adduser -S appuser -G appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose development server port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start development server with hot-reload
CMD ["npm", "start"]