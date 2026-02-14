# Production Deployment Guide

Comprehensive guide for deploying the Expense Tracker in a production environment.

## Overview

This guide covers deploying the Expense Tracker application in a production environment with focus on security, scalability, and reliability.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- At least 4GB RAM, 8GB recommended
- 50GB storage, 100GB recommended
- Domain name (optional but recommended)
- SSL certificate

## System Preparation

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop unzip

# Create application user
sudo adduser expense-tracker
sudo usermod -aG sudo expense-tracker
```

### 2. Install Dependencies

```bash
# Install Python 3.10
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Install Nginx
sudo apt install -y nginx

# Install Supervisor
sudo apt install -y supervisor
```

### 3. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Application Deployment

### 1. Clone Repository

```bash
# Switch to application user
sudo su - expense-tracker

# Clone application
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 3. Environment Configuration

```bash
# Create production environment file
cp .env.example .env.production
```

Edit `.env.production`:
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
MONGODB_URI=mongodb://localhost:27017/expense_tracker_prod
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216
```

### 4. Database Setup

```bash
# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database user
mongo
> use expense_tracker_prod
> db.createUser({
    user: "expense_user",
    pwd: "secure_password",
    roles: ["readWrite"]
  })
> exit

# Update MongoDB URI in .env.production
MONGODB_URI=mongodb://expense_user:secure_password@localhost:27017/expense_tracker_prod
```

### 5. Initialize Application

```bash
# Create database and collections
python create_db.py

# Create admin user
python manage.py create-admin
```

## Web Server Configuration

### 1. Gunicorn Configuration

Create `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "expense-tracker"
group = "expense-tracker"
tmp_upload_dir = None
logfile = "/home/expense-tracker/expense-tracker/logs/gunicorn.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

### 2. Supervisor Configuration

Create `/etc/supervisor/conf.d/expense-tracker.conf`:
```ini
[program:expense-tracker]
command=/home/expense-tracker/expense-tracker/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
directory=/home/expense-tracker/expense-tracker
user=expense-tracker
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/expense-tracker/expense-tracker/logs/supervisor.log
environment=PATH="/home/expense-tracker/expense-tracker/venv/bin"
```

Start the application:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start expense-tracker
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/expense-tracker`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Application Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static Files
    location /static {
        alias /home/expense-tracker/expense-tracker/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health Check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate Setup

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Auto-renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Logging

### 1. Log Rotation

Create `/etc/logrotate.d/expense-tracker`:
```
/home/expense-tracker/expense-tracker/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 expense-tracker expense-tracker
    postrotate
        supervisorctl restart expense-tracker
    endscript
}
```

### 2. Monitoring Setup

Install monitoring tools:
```bash
# Install Prometheus
sudo apt install -y prometheus

# Install Grafana
sudo apt install -y apt-transport-https
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt update
sudo apt install -y grafana
```

## Backup Strategy

### 1. Database Backup Script

Create `/home/expense-tracker/scripts/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/expense-tracker/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="expense_tracker_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --db $DB_NAME --out $BACKUP_DIR/mongodb_$DATE

# Compress backup
tar -czf $BACKUP_DIR/mongodb_$DATE.tar.gz -C $BACKUP_DIR mongodb_$DATE
rm -rf $BACKUP_DIR/mongodb_$DATE

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "mongodb_*.tar.gz" -mtime +30 -delete

echo "Backup completed: mongodb_$DATE.tar.gz"
```

Make it executable and add to cron:
```bash
chmod +x /home/expense-tracker/scripts/backup.sh
sudo crontab -e
# Add: 0 2 * * * /home/expense-tracker/scripts/backup.sh
```

## Security Hardening

### 1. System Security

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Change SSH port (optional)
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart ssh
```

### 2. Application Security

```bash
# Set proper file permissions
sudo chown -R expense-tracker:expense-tracker /home/expense-tracker/expense-tracker
sudo chmod 755 /home/expense-tracker/expense-tracker
sudo chmod 644 /home/expense-tracker/expense-tracker/.env.production
```

### 3. MongoDB Security

Edit `/etc/mongod.conf`:
```yaml
net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled
```

## Performance Optimization

### 1. Database Optimization

```javascript
// Create indexes in MongoDB
db.transactions.createIndex({ "date": -1 })
db.transactions.createIndex({ "category": 1, "date": -1 })
db.transactions.createIndex({ "account": 1, "date": -1 })
```

### 2. Application Caching

Add Redis caching:
```bash
sudo apt install -y redis-server
```

Update application configuration to use Redis for session storage.

## Health Checks

### 1. Application Health Check

Create `/home/expense-tracker/scripts/health-check.sh`:
```bash
#!/bin/bash

# Check if application is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Application is healthy"
    exit 0
else
    echo "Application is down"
    supervisorctl restart expense-tracker
    exit 1
fi
```

### 2. System Health Check

Add to cron:
```bash
sudo crontab -e
# Add: */5 * * * * /home/expense-tracker/scripts/health-check.sh
```

## Deployment Checklist

- [ ] Server secured and updated
- [ ] Firewall configured
- [ ] SSL certificate installed
- [ ] Application deployed and running
- [ ] Database configured with indexes
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Log rotation set up
- [ ] Health checks configured
- [ ] Performance optimized
- [ ] Security hardening completed

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check logs: `sudo supervisorctl tail expense-tracker`
   - Verify configuration files
   - Check database connection

2. **Nginx 502 errors**
   - Check if Gunicorn is running: `ps aux | grep gunicorn`
   - Verify Nginx configuration: `sudo nginx -t`
   - Check file permissions

3. **Database connection issues**
   - Verify MongoDB is running: `sudo systemctl status mongod`
   - Check authentication credentials
   - Test connection manually

### Performance Issues

1. **High memory usage**
   - Monitor with `htop`
   - Adjust Gunicorn workers
   - Check for memory leaks

2. **Slow database queries**
   - Enable MongoDB slow query log
   - Review and optimize indexes
   - Consider database scaling

This production deployment guide provides a comprehensive setup for running the Expense Tracker in a secure, scalable, and reliable production environment.
