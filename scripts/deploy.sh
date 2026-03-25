#!/bin/bash

# TrendNexAI Deployment Script
# Supports: Local Docker, Azure, AWS

set -e

ENVIRONMENT=${1:-development}
REGION=${2:-us-east-1}

echo "🚀 Deploying TrendNexAI to: $ENVIRONMENT (Region: $REGION)"

case "$ENVIRONMENT" in
  local)
    echo "📦 Starting local Docker deployment..."
    docker-compose -f docker-compose.yml up -d
    echo "✓ Local deployment complete"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "Docs: http://localhost:8000/docs"
    ;;

  development)
    echo "📦 Starting development deployment..."
    export ENV=development
    docker-compose -f docker-compose.yml up -d
    echo "✓ Development deployment complete"
    ;;

  production)
    echo "📦 Starting production deployment..."
    export ENV=production
    docker-compose -f docker-compose.yml up -d
    
    # Run database migrations
    docker-compose exec -T backend python -m alembic upgrade head
    
    # Create initial indexes
    docker-compose exec -T backend python -c "
    import asyncio
    from app.db_manager import initialize_database
    asyncio.run(initialize_database())
    "
    
    echo "✓ Production deployment complete"
    ;;

  azure)
    echo "🔷 Deploying to Azure..."
    
    # Check for Azure CLI
    if ! command -v az &> /dev/null; then
      echo "❌ Azure CLI not found. Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
      exit 1
    fi
    
    # Create resource group
    az group create \
      --name trendnexai-rg \
      --location eastus
    
    # Create container registry
    az acr create \
      --resource-group trendnexai-rg \
      --name trendnexairegistry \
      --sku Basic
    
    # Build and push images
    az acr build \
      --registry trendnexairegistry \
      --image trendnexai-backend:latest \
      --file backend/Dockerfile .
    
    az acr build \
      --registry trendnexairegistry \
      --image trendnexai-frontend:latest \
      --file Dockerfile .
    
    echo "✓ Azure deployment complete"
    echo "Registry: trendnexairegistry.azurecr.io"
    ;;

  aws)
    echo "🟠 Deploying to AWS..."
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
      echo "❌ AWS CLI not found. Install: https://aws.amazon.com/cli/"
      exit 1
    fi
    
    # Create ECR repositories
    aws ecr create-repository \
      --repository-name trendnexai-backend \
      --region $REGION || true
    
    aws ecr create-repository \
      --repository-name trendnexai-frontend \
      --region $REGION || true
    
    # Get ECR login
    aws ecr get-login-password --region $REGION | \
      docker login --username AWS --password-stdin \
      $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com
    
    # Build and push backend
    docker build -t trendnexai-backend:latest backend/
    docker tag trendnexai-backend:latest \
      $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/trendnexai-backend:latest
    docker push \
      $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/trendnexai-backend:latest
    
    # Build and push frontend
    docker build -t trendnexai-frontend:latest .
    docker tag trendnexai-frontend:latest \
      $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/trendnexai-frontend:latest
    docker push \
      $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/trendnexai-frontend:latest
    
    echo "✓ AWS ECR deployment complete"
    echo "Region: $REGION"
    ;;

  *)
    echo "❌ Unknown environment: $ENVIRONMENT"
    echo "Usage: ./deploy.sh [local|development|production|azure|aws] [region]"
    exit 1
    ;;
esac

echo "✅ Deployment complete!"
