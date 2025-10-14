# Use Node.js 18 LTS for building
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Create output directory for build artifacts
RUN mkdir -p /app/build_output

# Copy build artifacts to output directory
CMD ["cp", "-r", "build/*", "/app/build_output/"]
