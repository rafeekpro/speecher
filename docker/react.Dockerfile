# Multi-stage build for production React frontend
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY src/react-frontend/package*.json ./

# Install dependencies with legacy peer deps flag to handle version conflicts
RUN npm ci --legacy-peer-deps

# Copy source code
COPY src/react-frontend/ ./

# Build the application
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy nginx configuration
COPY docker/nginx.prod.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]