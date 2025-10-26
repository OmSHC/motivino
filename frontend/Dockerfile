# Use Node.js 20 LTS for building (required for React Router 7.9.3)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Create build output directory
RUN mkdir -p /app/build_output

# Default command: build and copy to mounted volume
CMD ["sh", "-c", "echo 'Starting frontend build process...' && npm run build && echo 'Build completed, copying to volume...' && ls -la build/ && cp -r build/* /app/build_output/ && echo '✅ Build files copied to volume:' && ls -la /app/build_output/ && echo '🎉 Frontend build complete!'"]
