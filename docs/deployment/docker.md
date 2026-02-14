# Docker Deployment

Deploy the Expense Tracker application using Docker containers.

## Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- At least 2GB RAM
- 5GB free disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

### 2. Build and Run

```bash
# Build the Docker image
docker build -t expense-tracker .

# Run the container
docker run -d \
  --name expense-tracker \
  -p 5000:5000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/expense_tracker \
  -e SECRET_KEY=your-secret-key-here \
  expense-tracker
```

### 3. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Dockerfile Analysis

The application includes a multi-stage Dockerfile:

```dockerfile
# Build stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

## Docker Compose Configuration

### Basic Setup

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/expense_tracker
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    depends_on:
      - mongo
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}

volumes:
  mongo_data:
```

### Production Setup with Nginx

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app

  app:
    build: .
    expose:
      - "5000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/expense_tracker
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    depends_on:
      - mongo
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups

  mongo:
    image: mongo:6.0
    expose:
      - "27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}

volumes:
  mongo_data:
```

## Environment Configuration

Create a `.env` file:

```env
SECRET_KEY=your-very-secure-secret-key-here
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=secure-mongo-password
FLASK_ENV=production
DEBUG=False
```

## Production Optimizations

### 1. Multi-Stage Build

Optimize image size with multi-stage builds:

```dockerfile
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
EXPOSE 5000
USER nobody
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### 2. Health Checks

Add health checks to your Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

### 3. Resource Limits

Set resource limits in docker-compose:

```yaml
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Volume Management

### Persistent Data

```yaml
volumes:
  mongo_data:
    driver: local
  app_logs:
    driver: local
  app_backups:
    driver: local
```

### Backup Strategy

```bash
# Backup MongoDB
docker exec mongo mongodump --out /backup

# Backup application data
docker run --rm -v expense-tracker_app_backups:/data -v $(pwd):/backup alpine tar czf /backup/app-backup.tar.gz -C /data .
```

## Monitoring & Logging

### Logging Configuration

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring with Prometheus

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Security Considerations

### 1. Non-Root User

```dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

### 2. Read-only Filesystem

```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
```

### 3. Secrets Management

```yaml
secrets:
  mongo_password:
    file: ./secrets/mongo_password.txt
  app_secret_key:
    file: ./secrets/app_secret_key.txt

services:
  app:
    secrets:
      - mongo_password
      - app_secret_key
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker logs expense-tracker
   
   # Check container status
   docker ps -a
   ```

2. **Database connection issues**
   ```bash
   # Test MongoDB connection
   docker exec mongo mongo --eval "db.adminCommand('ismaster')"
   ```

3. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :5000
   ```

### Debug Mode

Run container in debug mode:

```bash
docker run -it --rm \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  -e DEBUG=True \
  expense-tracker
```

## Performance Tuning

### 1. Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### 2. Nginx Configuration

```nginx
upstream app {
    server app:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets properly secured
- [ ] Health checks enabled
- [ ] Resource limits set
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Log rotation configured
- [ ] Performance testing completed
