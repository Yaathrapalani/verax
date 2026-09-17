# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install npm dependencies reproducibly
RUN npm ci

# Copy frontend source code
COPY . .

# Build production static assets
RUN npm run build

# Serve stage using lightweight static server
FROM nginx:alpine

# Copy custom nginx configuration if needed or use default html folder
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/index.html || exit 1

CMD ["nginx", "-g", "daemon off;"]
