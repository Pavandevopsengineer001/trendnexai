# 🚀 Production Deployment Guide for TrendNexAI

## Azure App Service Deployment

### Prerequisites
- Azure Account
- Azure CLI installed
- Docker Hub account (or Azure Container Registry)

### Step-by-Step Deployment

#### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name trendnexai-prod \
  --location eastus

# Create Azure Container Registry
az acr create \
  --resource-group trendnexai-prod \
  --name trendnexairegistry \
  --sku Basic

# Create App Service Plan
az appservice plan create \
  --name trendnexai-plan \
  --resource-group trendnexai-prod \
  --sku B2 \
  --is-linux

# Create App Service for Backend
az webapp create \
  --resource-group trendnexai-prod \
  --plan trendnexai-plan \
  --name trendnexai-api \
  --deployment-container-image-name-user admin \
  --deployment-container-image-name trendnexai-backend:latest \
  --registry-server-user <username> \
  --registry-server-password <password>

# Create App Service for Frontend
az webapp create \
  --resource-group trendnexai-prod \
  --plan trendnexai-plan \
  --name trendnexai-web \
  --deployment-container-image-name-user admin \
  --deployment-container-image-name trendnexai-frontend:latest \
  --registry-server-user <username> \
  --registry-server-password <password>
```

#### 2. Configure Environment Variables

```bash
# Backend environment variables
az webapp config appsettings set \
  --resource-group trendnexai-prod \
  --name trendnexai-api \
  --settings \
    ENV=production \
    MONGODB_URI="<your-mongodb-uri>" \
    REDIS_URL="<your-redis-connection-string>" \
    SECRET_KEY="<generate-secure-key>" \
    OPENAI_API_KEY="<your-openai-key>" \
    NEWS_API_KEY="<your-newsapi-key>"

# Frontend environment variables
az webapp config appsettings set \
  --resource-group trendnexai-prod \
  --name trendnexai-web \
  --settings \
    NEXT_PUBLIC_API_URL="https://trendnexai-api.azurewebsites.net" \
    NEXT_PUBLIC_SITE_URL="https://trendnexai-web.azurewebsites.net"
```

#### 3. Setup MongoDB Atlas

```bash
# Create MongoDB Atlas cluster (via web console)
# 1. Go to https://www.mongodb.com/cloud/atlas
# 2. Create cluster in Azure - East US region
# 3. Get connection string
# 4. Use in MONGODB_URI environment variable
```

#### 4. Setup Azure Cache for Redis

```bash
az redis create \
  --resource-group trendnexai-prod \
  --name trendnexai-redis \
  --location eastus \
  --sku Premium \
  --vm-size c0

# Get Redis connection string
az redis show-connection-string \
  --name trendnexai-redis \
  --resource-group trendnexai-prod
```

#### 5. Deploy Docker Images

```bash
# Build and push to Azure Container Registry
az acr build \
  --registry trendnexairegistry \
  --image trendnexai-backend:latest \
  --file backend/Dockerfile .

az acr build \
  --registry trendnexairegistry \
  --image trendnexai-frontend:latest \
  --file Dockerfile .

# Enable admin user
az acr update \
  --name trendnexairegistry \
  --admin-enabled true
```

#### 6. Configure CI/CD

```bash
# Enable continuous deployment from registry
az webapp deployment container config \
  --name trendnexai-api \
  --resource-group trendnexai-prod \
  --enable-cd true

az webapp deployment container config \
  --name trendnexai-web \
  --resource-group trendnexai-prod \
  --enable-cd true
```

#### 7. Setup Custom Domain & SSL

```bash
# Bind custom domain
az webapp config hostname add \
  --resource-group trendnexai-prod \
  --webapp-name trendnexai-api \
  --hostname api.yourdomain.com

az webapp config hostname add \
  --resource-group trendnexai-prod \
  --webapp-name trendnexai-web \
  --hostname yourdomain.com

# Enable HTTPS/SSL (auto - handled by Azure)
az webapp config ssl bind \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI \
  --name trendnexai-api \
  --resource-group trendnexai-prod
```

---

## AWS ECS Deployment

### Prerequisites
- AWS Account
- AWS CLI configured
- Docker installed

### Step-by-Step Deployment

#### 1. Create AWS Infrastructure

```bash
# Create VPC security group
aws ec2 create-security-group \
  --group-name trendnexai-sg \
  --description "Security group for TrendNexAI" \
  --vpc-id <vpc-id>

# Allow inbound traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

#### 2. Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name trendnexai-prod \
  --region us-east-1

# Create CloudWatch log groups
aws logs create-log-group \
  --log-group-name /ecs/trendnexai-backend \
  --region us-east-1

aws logs create-log-group \
  --log-group-name /ecs/trendnexai-frontend \
  --region us-east-1
```

#### 3. Create ECR Repositories

```bash
# Create repositories
aws ecr create-repository \
  --repository-name trendnexai-backend \
  --region us-east-1

aws ecr create-repository \
  --repository-name trendnexai-frontend \
  --region us-east-1

# Get login token and push images
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t trendnexai-backend:latest backend/
docker tag trendnexai-backend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/trendnexai-backend:latest
docker push \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/trendnexai-backend:latest
```

#### 4. Setup RDS & ElastiCache

```bash
# Create RDS MongoDB cluster
aws docdb create-db-cluster \
  --db-cluster-identifier trendnexai-db \
  --engine docdb \
  --master-username admin \
  --master-password <strong-password>

# Create ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id trendnexai-redis \
  --cache-node-type cache.t3.small \
  --engine redis \
  --num-cache-nodes 1
```

#### 5. Create ECS Task Definitions

```bash
# Backend task definition
cat > backend-task.json <<EOF
{
  "family": "trendnexai-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "trendnexai-backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/trendnexai-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENV", "value": "production"},
        {"name": "MONGODB_URI", "value": "<docdb-connection-string>"},
        {"name": "REDIS_URL", "value": "<redis-connection-string>"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trendnexai-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://backend-task.json
```

#### 6. Create ECS Services

```bash
# Backend service
aws ecs create-service \
  --cluster trendnexai-prod \
  --service-name trendnexai-backend \
  --task-definition trendnexai-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

#### 7. Setup Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name trendnexai-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx

# Create target groups
aws elbv2 create-target-group \
  --name trendnexai-backend \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx
```

---

## Monitoring & Maintenance

### Azure Monitoring

```bash
# View application logs
az webapp log tail \
  --resource-group trendnexai-prod \
  --name trendnexai-api

# Setup alerts
az monitor metrics alert create \
  --name HighCPU \
  --resource-group trendnexai-prod \
  --scopes /subscriptions/<id>/resourceGroups/trendnexai-prod/providers/Microsoft.Web/sites/trendnexai-api \
  --condition "avg Percentage CPU > 80" \
  --action <action-group-id>
```

### AWS CloudWatch Monitoring

```bash
# View logs
aws logs tail /ecs/trendnexai-backend --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name trendnexai-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 60 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## Scaling Considerations

### Horizontal Scaling
- Use auto-scaling groups
- Set min: 2, max: 10 instances
- CPU threshold: 70%

### Vertical Scaling
- Database: Upgrade to larger instance
- Cache: Increase Redis tier
- Compute: Move to larger container size

### CDN & Caching
- Use CloudFront (AWS) or Azure CDN
- Cache static assets (images, CSS, JS)
- Cache API responses for 5 minutes

---

## Cost Optimization

- Use reserved instances (30% savings)
- Setup auto-shutdown for dev environments
- Use spot instances for non-critical workers
- Monitor and optimize database queries
- Enable compression for API responses
