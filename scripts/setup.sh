#!/bin/bash

# TrendNexAI Setup and Development Environment

set -e

echo "🔧 Setting up TrendNexAI development environment..."

# Create .env file if not exists
if [ ! -f .env ]; then
  echo "📝 Creating .env file..."
  cp .env.example .env
  echo "⚠️  Please update .env with your API keys"
fi

# Create backend .env if not exists
if [ ! -f backend/.env ]; then
  echo "📝 Creating backend/.env file..."
  cp backend/.env.example backend/.env
fi

# Create frontend .env if not exists
if [ ! -f .env.local ]; then
  echo "📝 Creating .env.local file..."
  cp .env.frontend.example .env.local
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
  echo "✓ Docker found"
  
  # Start containers
  echo "🐳 Starting Docker containers..."
  docker-compose up -d
  
  echo ""
  echo "✅ Services started:"
  echo "  MongoDB: localhost:27017"
  echo "  Redis: localhost:6379"
  echo "  Backend: http://localhost:8000"
  echo "  Frontend: http://localhost:3000"
else
  echo "ℹ️  Docker not found. Setting up local development environment..."
  
  # Python setup
  if command -v python3 &> /dev/null; then
    echo "✓ Python 3 found"
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
  fi
  
  # Node setup
  if command -v npm &> /dev/null; then
    echo "✓ npm found"
    echo "📦 Installing Node packages..."
    npm install
  fi
fi

echo ""
echo "📚 Next steps:"
echo "  1. Update .env with your API keys (OpenAI, NewsAPI, etc.)"
echo "  2. Start the application:"
echo "     - With Docker: docker-compose up -d"
echo "     - Locally: npm run dev (frontend) & uvicorn app.main:app --reload (backend)"
echo "  3. Access admin dashboard: http://localhost:3000/admin"
echo ""
echo "✅ Setup complete!"
