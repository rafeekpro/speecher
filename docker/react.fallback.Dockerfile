# Fallback Dockerfile for Docker Hub availability issues  
# Uses non-alpine images for maximum stability during outages

# Build stage - Using standard Node.js (non-alpine) for maximum stability
FROM node:18 AS build

WORKDIR /app

# Copy package files
COPY src/react-frontend/package*.json ./

# Install all dependencies (including devDependencies for build)
# Using --legacy-peer-deps to handle TypeScript version conflicts with react-scripts
RUN npm ci --legacy-peer-deps

# Copy source code
COPY src/react-frontend/ ./

# Build the React app
RUN npm run build

# Production stage - using standard nginx (not alpine) for stability
FROM nginx:stable

# Copy built React app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Custom nginx configuration for React Router
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]