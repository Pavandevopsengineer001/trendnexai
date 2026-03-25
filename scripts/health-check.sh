#!/bin/bash

# Health check script for production monitoring

BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}

echo "🔍 Running health checks..."

# Backend health
echo -n "Backend API: "
if curl -s "$BACKEND_URL/health" | grep -q "healthy"; then
  echo "✓ OK"
else
  echo "✗ FAILED"
  exit 1
fi

# Frontend health
echo -n "Frontend: "
if curl -s "$FRONTEND_URL" | grep -q "html" > /dev/null 2>&1; then
  echo "✓ OK"
else
  echo "✗ FAILED"
  exit 1
fi

# MongoDB connection
echo -n "MongoDB: "
if docker exec trendnexai-mongodb mongosh admin -u admin -p password --eval 'db.runCommand({ping:1})' > /dev/null 2>&1; then
  echo "✓ OK"
else
  echo "✗ FAILED"
fi

# Redis connection
echo -n "Redis: "
if docker exec trendnexai-redis redis-cli ping > /dev/null 2>&1; then
  echo "✓ OK"
else
  echo "✗ FAILED"
fi

echo ""
echo "✅ All systems operational!"
