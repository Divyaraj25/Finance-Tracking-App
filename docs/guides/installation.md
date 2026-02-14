# Installation Guide

Detailed installation instructions for the Expense Tracker application.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **MongoDB**: 6.0 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **MongoDB**: 6.0+ with WiredTiger storage engine
- **RAM**: 8GB or more
- **Storage**: 5GB free space

## Installation Methods

### Method 1: Standard Installation

#### 1. Install Python

**Windows:**
```bash
# Download from python.org or use winget
winget install Python.Python.3.10
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.10
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-pip python3.10-venv
```

#### 2. Install MongoDB

**Windows:**
```bash
# Download and install from mongodb.com
# Or using Chocolatey
choco install mongodb
```

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
```

#### 3. Clone and Setup Application

```bash
# Clone the repository
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit the configuration
nano .env  # or use your preferred editor
```

Required configuration:
```env
MONGODB_URI=mongodb://localhost:27017/expense_tracker
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=development
DEBUG=True
```

#### 5. Initialize Database

```bash
# Create database and collections
python create_db.py

# Run database migrations if needed
python manage.py migrate
```

#### 6. Start the Application

```bash
python run.py
```

### Method 2: Docker Installation

#### 1. Install Docker

Install Docker Desktop for your operating system from [docker.com](https://docker.com)

#### 2. Clone and Run

```bash
# Clone the repository
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker

# Build and run with Docker Compose
docker-compose up -d
```

The application will be available at `http://localhost:5000`

### Method 3: Development Setup

For developers who want to contribute:

```bash
# Clone with development dependencies
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/

# Start development server with auto-reload
python run.py --debug
```

## Post-Installation Setup

### 1. Create Admin User

```bash
python manage.py create-admin
```

### 2. Configure Email Settings (Optional)

Add to `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Set Up Backup Schedule (Optional)

```bash
# Add to crontab for daily backups
0 2 * * * /path/to/expense-tracker/scripts/backup.sh
```

## Verification

### Check Application Status

```bash
# Check if application is running
curl http://localhost:5000/health

# Check database connection
python -c "from app import db; print('Database connected:', db.engine.execute('SELECT 1').scalar())"
```

### Test API Endpoints

```bash
# Test API health
curl http://localhost:5000/api/v1/health

# Test authentication
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   
   # Start MongoDB
   sudo systemctl start mongod
   ```

2. **Python Module Not Found**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   
   # Kill the process
   kill -9 <PID>
   ```

4. **Permission Denied**
   ```bash
   # Fix file permissions
   chmod +x scripts/*.sh
   ```

### Getting Help

- Check the [troubleshooting guide](./troubleshooting.md)
- Review the [FAQ](./faq.md)
- Create an issue on GitHub with:
  - Operating system and version
  - Python version
  - MongoDB version
  - Complete error message
  - Steps to reproduce
