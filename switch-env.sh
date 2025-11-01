#!/bin/bash

# Script to switch between development and production configurations

if [ "$1" = "dev" ]; then
    echo "🔧 DEVELOPMENT Environment Setup"
    echo "=================================="
    echo "   ✅ SQLite database (no PostgreSQL needed)"
    echo "   ✅ Redis for caching"
    echo "   ✅ Django backend + React frontend"
    echo "   ✅ Hot reload for frontend development"
    echo ""
    echo "📁 Using: docker-compose.yml"
    echo "🌐 Frontend: http://localhost (nginx serves built React app)"
    echo "🔗 Backend API: http://localhost/api"
    echo ""
    echo "🚀 To start development:"
    echo "   docker-compose up --build"
    echo ""
    echo "💡 Frontend development (hot reload):"
    echo "   cd frontend && npm start"
    echo "   Then visit: http://localhost:3000"

elif [ "$1" = "prod" ]; then
    echo "🚀 PRODUCTION Environment Setup"
    echo "================================="
    echo "   ✅ SQLite database (file-based)"
    echo "   ✅ Redis for caching"
    echo "   ✅ Optimized for GCP deployment"
    echo "   ✅ HTTPS with SSL certificates"
    echo ""
    echo "📁 Using: docker-compose.prod.yml"
    echo "🌐 Access: https://your-domain.com"
    echo ""
    echo "🚀 To deploy:"
    echo "   docker-compose -f docker-compose.prod.yml up --build -d"
    echo ""
    echo "📦 Pre-built images available:"
    echo "   docker-compose -f docker-compose.gcp.yml pull"

else
    echo "Usage: $0 [dev|prod]"
    echo ""
    echo "  dev  - Development environment (HTTP, hot reload)"
    echo "  prod - Production environment (HTTPS, optimized)"
    echo ""
    echo "Available Docker Compose files:"
    echo "  📁 docker-compose.yml        - Development (4 containers)"
    echo "  📁 docker-compose.prod.yml   - Production (4 containers)"
    echo "  📁 docker-compose.gcp.yml    - GCP deployment (3 containers)"
    echo "  📁 docker-compose.simple.yml - Simple dev (2 containers)"
    echo ""
    echo "Database: SQLite (no PostgreSQL needed!)"
fi
