# Stage 1: Build the frontend app
FROM node:22-slim AS build

# Set working directory
WORKDIR /app

# Copy package definition and lock file first (to cache deps separately)
COPY package.json package-lock.json ./

# Install dependencies (including devDependencies for build tools)
RUN npm ci

# Copy the rest of the frontend source code
COPY . .

# Build the frontend app (output to /app/dist or similar)
RUN npm run build

# Stage 2: Serve static files with a minimal Nginx image
FROM nginx:alpine AS production

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage to Nginx's default HTML dir
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the port (Nginx default is 80)
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
