# AWS Deployment Guide

This guide covers multiple AWS deployment options for the Content Service API.

---

## Table of Contents

1. [AWS App Runner (Easiest)](#1-aws-app-runner-easiest)
2. [AWS ECS with Fargate (Recommended)](#2-aws-ecs-with-fargate-recommended)
3. [AWS Elastic Beanstalk](#3-aws-elastic-beanstalk)
4. [AWS EC2 with Docker](#4-aws-ec2-with-docker)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Post-Deployment Steps](#post-deployment-steps)

---

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- AWS RDS PostgreSQL database (already set up)

---

## 1. AWS App Runner (Easiest)

App Runner automatically builds and deploys from source or container image.

### Using Docker Hub or ECR

**Step 1: Build and push Docker image**

```bash
# Login to Amazon ECR
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name content-service --region ap-southeast-2

# Build image
docker build -t content-service .

# Tag image
docker tag content-service:latest <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest

# Push to ECR
docker push <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest
```

**Step 2: Create App Runner service**

1. Go to **AWS App Runner** console
2. Click **Create service**
3. Choose **Container registry** → **Amazon ECR**
4. Select your image
5. Set **Port**: `8080`
6. Add environment variables (see [Environment Variables](#environment-variables))
7. Click **Create & deploy**

**Step 3: Run migrations**

Connect to your App Runner service and run:
```bash
# Use AWS Systems Manager Session Manager or execute via task
alembic upgrade head
python seed_data.py
```

---

## 2. AWS ECS with Fargate (Recommended)

Production-ready container orchestration with auto-scaling.

### Step 1: Push Docker Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name content-service --region ap-southeast-2

# Get ECR login
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com

# Build and push
docker build -t content-service .
docker tag content-service:latest <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest
docker push <account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest
```

### Step 2: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name content-service-cluster --region ap-southeast-2
```

### Step 3: Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "content-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "content-service",
      "image": "<account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:VyonDev2026@vyon-curriculum-database-dev.czqq8my4uutx.ap-southeast-2.rds.amazonaws.com:5432/postgres"
        },
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/content-service",
          "awslogs-region": "ap-southeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### Step 4: Create Application Load Balancer

1. Go to **EC2** → **Load Balancers** → **Create Load Balancer**
2. Choose **Application Load Balancer**
3. Configure:
   - Name: `content-service-alb`
   - Scheme: Internet-facing
   - VPC: Same as RDS
   - Subnets: Select at least 2 public subnets
4. Create target group:
   - Target type: IP
   - Protocol: HTTP
   - Port: 8080
   - Health check path: `/health`
5. Create load balancer

### Step 5: Create ECS Service

```bash
aws ecs create-service \
  --cluster content-service-cluster \
  --service-name content-service \
  --task-definition content-service \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:ap-southeast-2:<account-id>:targetgroup/content-service/xxx,containerName=content-service,containerPort=8080" \
  --region ap-southeast-2
```

### Step 6: Run Migrations

Create a one-time task to run migrations:

```bash
aws ecs run-task \
  --cluster content-service-cluster \
  --task-definition content-service \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"content-service","command":["alembic","upgrade","head"]}]}' \
  --region ap-southeast-2
```

Then seed:
```bash
aws ecs run-task \
  --cluster content-service-cluster \
  --task-definition content-service \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"content-service","command":["python","seed_data.py"]}]}' \
  --region ap-southeast-2
```

---

## 3. AWS Elastic Beanstalk

Simple PaaS deployment with automatic scaling.

### Step 1: Install EB CLI

```bash
pip install awsebcli
```

### Step 2: Initialize Elastic Beanstalk

```bash
eb init -p docker content-service --region ap-southeast-2
```

### Step 3: Create Dockerrun.aws.json

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "<account-id>.dkr.ecr.ap-southeast-2.amazonaws.com/content-service:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8080,
      "HostPort": 8080
    }
  ]
}
```

### Step 4: Create Environment

```bash
eb create content-service-env \
  --instance-type t3.small \
  --envvars DATABASE_URL="postgresql://postgres:VyonDev2026@vyon-curriculum-database-dev.czqq8my4uutx.ap-southeast-2.rds.amazonaws.com:5432/postgres"
```

### Step 5: Deploy

```bash
eb deploy
```

### Step 6: SSH and run migrations

```bash
eb ssh
docker exec -it $(docker ps -q) alembic upgrade head
docker exec -it $(docker ps -q) python seed_data.py
```

---

## 4. AWS EC2 with Docker

Traditional VM deployment with full control.

### Step 1: Launch EC2 Instance

1. Go to **EC2** → **Launch Instance**
2. Choose **Amazon Linux 2023** AMI
3. Instance type: **t3.small** or **t3.medium**
4. Configure security group:
   - SSH (22) from your IP
   - HTTP (8080) from anywhere
5. Launch with key pair

### Step 2: Connect and Install Docker

```bash
ssh -i your-key.pem ec2-user@<ec2-public-ip>

# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again
exit
ssh -i your-key.pem ec2-user@<ec2-public-ip>

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Clone and Deploy

```bash
# Install git
sudo yum install git -y

# Clone repository
git clone https://github.com/Vrushi007/school-ai.content.api.git
cd school-ai.content.api

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:VyonDev2026@vyon-curriculum-database-dev.czqq8my4uutx.ap-southeast-2.rds.amazonaws.com:5432/postgres
ENVIRONMENT=production
EOF

# Build and run
docker build -t content-service .
docker run -d --name content-service -p 8080:8080 --env-file .env content-service

# Run migrations
docker exec content-service alembic upgrade head
docker exec content-service python seed_data.py
```

### Step 4: Set up Auto-restart

```bash
# Update container to always restart
docker update --restart unless-stopped content-service
```

---

## Environment Variables

Required environment variables for all deployments:

```bash
DATABASE_URL=postgresql://postgres:VyonDev2026@vyon-curriculum-database-dev.czqq8my4uutx.ap-southeast-2.rds.amazonaws.com:5432/postgres
ENVIRONMENT=production
AI_SERVICE_URL=http://your-ai-service-url:8000  # Optional, for lesson planning features
ALLOWED_ORIGINS=https://yourdomain.com  # Optional, for CORS in production
```

---

## Database Setup

Your RDS database is already configured:
- **Endpoint**: `vyon-curriculum-database-dev.czqq8my4uutx.ap-southeast-2.rds.amazonaws.com`
- **Port**: 5432
- **Database**: postgres
- **Region**: ap-southeast-2 (Sydney)

### Security Group Requirements

Ensure your RDS security group allows inbound traffic:
- **From ECS/EC2 security group** (if using private subnet)
- **From 0.0.0.0/0** on port 5432 (if public, not recommended for production)

---

## Post-Deployment Steps

### 1. Run Database Migrations

```bash
# ECS
aws ecs run-task ... --overrides '{"containerOverrides":[{"name":"content-service","command":["alembic","upgrade","head"]}]}'

# EC2
docker exec content-service alembic upgrade head

# App Runner / Elastic Beanstalk
# SSH into instance and run migrations
```

### 2. Seed Database

```bash
# ECS
aws ecs run-task ... --overrides '{"containerOverrides":[{"name":"content-service","command":["python","seed_data.py"]}]}'

# EC2
docker exec content-service python seed_data.py
```

### 3. Verify Deployment

```bash
# Health check
curl http://<your-endpoint>/health

# Get states
curl http://<your-endpoint>/states

# API Documentation
open http://<your-endpoint>/docs
```

### 4. Set Up Domain (Optional)

1. Go to **Route 53** → Create hosted zone
2. Create **A record** pointing to:
   - ALB DNS (for ECS)
   - EC2 public IP (for EC2)
   - App Runner URL (for App Runner)
3. Update `ALLOWED_ORIGINS` environment variable with your domain

### 5. Enable HTTPS (Recommended)

**For ALB (ECS):**
1. Request certificate in **AWS Certificate Manager**
2. Add HTTPS listener to ALB
3. Update security groups

**For EC2:**
```bash
# Install Nginx
sudo yum install nginx -y

# Configure reverse proxy with Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

---

## Monitoring and Logs

### CloudWatch Logs

Logs are automatically sent to CloudWatch:
- ECS: `/ecs/content-service`
- Elastic Beanstalk: `/aws/elasticbeanstalk/content-service-env`
- App Runner: Automatic logging

### Viewing Logs

```bash
# AWS CLI
aws logs tail /ecs/content-service --follow

# ECS Console
# Go to ECS → Clusters → Service → Tasks → Logs tab
```

### Metrics and Alarms

Set up CloudWatch alarms for:
- CPU utilization > 80%
- Memory utilization > 80%
- HTTP 5xx errors > 10
- Health check failures

---

## Scaling

### ECS Auto Scaling

```bash
# Create auto-scaling policy
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/content-service-cluster/content-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# CPU-based scaling
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --resource-id service/content-service-cluster/content-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## Cost Optimization

### Estimated Monthly Costs (ap-southeast-2)

- **App Runner**: ~$15-30 (0.25 vCPU, 0.5 GB memory)
- **ECS Fargate**: ~$25-40 (2 tasks, 0.5 vCPU, 1 GB each)
- **Elastic Beanstalk**: ~$20-35 (t3.small)
- **EC2 (t3.small)**: ~$15-25
- **RDS db.t3.micro**: ~$15-20

**Total**: $30-60/month for small production deployment

### Savings Tips

1. Use **Savings Plans** or **Reserved Instances** for EC2/RDS
2. Enable **auto-scaling** to scale down during low traffic
3. Use **Fargate Spot** for non-critical workloads
4. Stop dev/test environments when not in use

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
aws ecs describe-tasks --cluster content-service-cluster --tasks <task-id>

# Check container logs
aws logs tail /ecs/content-service --follow
```

### Database Connection Issues

1. Check security groups allow traffic from ECS/EC2
2. Verify DATABASE_URL is correct
3. Test connection: `docker exec content-service psql $DATABASE_URL`

### Migration Failures

```bash
# Check current migration version
docker exec content-service alembic current

# Rollback
docker exec content-service alembic downgrade -1

# Re-run
docker exec content-service alembic upgrade head
```

---

## CI/CD Pipeline (Optional)

Use **AWS CodePipeline** or **GitHub Actions** for automated deployments:

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-2
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: content-service
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster content-service-cluster \
            --service content-service --force-new-deployment
```

---

## Support

For issues or questions:
- Check CloudWatch logs
- Review AWS documentation
- Open GitHub issue

**Happy Deploying! 🚀**
