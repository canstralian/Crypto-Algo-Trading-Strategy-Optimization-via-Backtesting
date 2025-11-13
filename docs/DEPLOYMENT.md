# Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+ (for local development)
- Git

## Local Development

### 1. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configuration

```bash
# Copy configuration files
cp config/config.example.yaml config/config.yaml
cp .env.example .env

# Edit configuration
vim config/config.yaml
vim .env
```

### 3. Run Development Server

```bash
# Start API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Access API
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t crypto-trading-platform:latest .

# Run container
docker run -d \
  --name trading-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config:ro \
  -e ENVIRONMENT=production \
  crypto-trading-platform:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## Production Deployment

### Prerequisites

- Domain name
- SSL certificate (Let's Encrypt)
- Cloud provider (AWS, GCP, Azure, etc.)

### Option 1: Docker on VM

1. **Provision VM**
```bash
# Create VM with Ubuntu 22.04
# Minimum: 2 vCPU, 4GB RAM, 20GB SSD
```

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Deploy Application**
```bash
# Clone repository
git clone <repository-url>
cd crypto-trading-platform

# Setup environment
cp .env.example .env
vim .env  # Configure production settings

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

4. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. **SSL with Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Option 2: Kubernetes

1. **Create Kubernetes Manifests**

See `deployment/kubernetes/` directory for:
- `deployment.yaml`
- `service.yaml`
- `ingress.yaml`
- `configmap.yaml`
- `secret.yaml`

2. **Deploy to Kubernetes**
```bash
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods
kubectl get services
kubectl get ingress

# View logs
kubectl logs -f deployment/trading-api
```

### Option 3: Cloud Platforms

#### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag crypto-trading-platform:latest \
  <account>.dkr.ecr.us-east-1.amazonaws.com/trading-platform:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/trading-platform:latest

# Create ECS task definition and service
aws ecs create-service --cli-input-json file://ecs-service.json
```

#### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/trading-platform

# Deploy to Cloud Run
gcloud run deploy trading-api \
  --image gcr.io/<project-id>/trading-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-trading-platform

# Deploy
git push heroku main

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO
```

## Environment Variables

### Required

```bash
ENVIRONMENT=production
SECRET_KEY=<random-secret-key>
LOG_LEVEL=INFO
```

### Optional

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# Monitoring
SENTRY_DSN=<sentry-dsn>

# API Keys (for live trading)
BINANCE_API_KEY=<key>
BINANCE_SECRET_KEY=<secret>
```

## Database Setup

### PostgreSQL

```bash
# Using Docker
docker run -d \
  --name trading-postgres \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=trader \
  -e POSTGRES_PASSWORD=<password> \
  -v postgres-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

# Run migrations
alembic upgrade head
```

## Monitoring Setup

### Prometheus & Grafana

```bash
# Add to docker-compose.yml
docker-compose -f docker-compose.monitoring.yml up -d
```

### Log Aggregation

```bash
# Configure log shipping to:
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - Datadog
# - CloudWatch
```

## Backup Strategy

### Data Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Upload to S3
aws s3 cp backup-*.tar.gz s3://your-bucket/backups/
```

### Database Backup

```bash
# PostgreSQL backup
pg_dump trading_db > backup.sql

# Restore
psql trading_db < backup.sql
```

## Health Checks

### Application Health

```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00Z",
#   "version": "1.0.0"
# }
```

### Docker Health

```bash
docker ps
# Check HEALTH column shows (healthy)
```

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale trading-api=3

# Kubernetes
kubectl scale deployment trading-api --replicas=3
```

### Vertical Scaling

Update resource limits in:
- `docker-compose.yml`
- `deployment/kubernetes/deployment.yaml`

## SSL/TLS Configuration

### Let's Encrypt

```bash
certbot certonly --standalone -d api.yourdomain.com
```

### Custom Certificate

```bash
# Add to nginx config
ssl_certificate /etc/ssl/certs/your-cert.pem;
ssl_certificate_key /etc/ssl/private/your-key.pem;
```

## Performance Tuning

### Application

```yaml
# config/config.yaml
api:
  workers: 4
  timeout: 60

performance:
  use_multiprocessing: true
  max_workers: 4
```

### Database

```sql
-- Create indexes
CREATE INDEX idx_timestamp ON ohlcv_data(timestamp);
CREATE INDEX idx_symbol ON ohlcv_data(symbol);
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs trading-api

# Check resources
docker stats

# Inspect container
docker inspect trading-api
```

### High Memory Usage

```bash
# Limit memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Connection Issues

```bash
# Check network
docker network ls
docker network inspect trading-network

# Test connectivity
docker exec trading-api ping postgres
```

## Security Checklist

- [ ] Change default passwords
- [ ] Use environment variables for secrets
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Implement authentication
- [ ] Setup monitoring and alerts
- [ ] Regular backups
- [ ] Audit logs enabled

## Rollback Procedure

```bash
# Docker
docker-compose down
docker-compose pull
docker-compose up -d --force-recreate

# Kubernetes
kubectl rollout undo deployment/trading-api
kubectl rollout status deployment/trading-api
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Or zero-downtime update
docker-compose up -d --no-deps --build trading-api
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```
