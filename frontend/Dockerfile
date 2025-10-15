# Use Node.js 20 LTS for building (required for React Router 7.9.3)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci

# Copy source code
COPY . .

# Create build output directory
RUN mkdir -p /app/build_output

# Default command: build and copy to output directory
CMD ["sh", "-c", "echo 'Building React app...' && npm run build && echo 'Copying build files...' && cp -r build/* /app/build_output/ && echo 'Frontend build complete!'"]
