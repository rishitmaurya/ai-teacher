"""
Production deployment guide for FastAPI Text-to-Speech backend
Includes examples for Windows, Linux, Docker, and Cloud platforms
"""

# =============================================================================
# WINDOWS DEPLOYMENT
# =============================================================================

## Development Mode
python main.py

## Production Mode with Gunicorn
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile - --error-logfile -

## Using Windows Service (NSSM - Non-Sucking Service Manager)
# Download NSSM from https://nssm.cc/download
# nssm install TTSBackend "C:\path\to\venv39\Scripts\python.exe" "main.py"
# nssm start TTSBackend


# =============================================================================
# LINUX/MAC DEPLOYMENT
# =============================================================================

## Install and run with systemd

# 1. Create service file
sudo tee /etc/systemd/system/ai-teacher-tts.service > /dev/null <<EOF
[Unit]
Description=AI Teacher Text-to-Speech Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-teach-old
Environment="PATH=/path/to/ai-teach-old/venv39/bin"
ExecStart=/path/to/ai-teach-old/venv39/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 2. Enable and start service
sudo systemctl enable ai-teacher-tts
sudo systemctl start ai-teacher-tts

# 3. Check status
sudo systemctl status ai-teacher-tts

# 4. View logs
sudo journalctl -u ai-teacher-tts -f


# =============================================================================
# DOCKER DEPLOYMENT
# =============================================================================

## Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY config.json .
COPY client.js .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


## Docker Build and Run
docker build -t ai-teacher-tts:1.0 .
docker run -d --name ai-teacher-tts -p 8000:8000 ai-teacher-tts:1.0

## Docker Compose
version: '3.8'
services:
  tts-backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config.json:/app/config.json
    environment:
      - LOG_LEVEL=info
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3


# =============================================================================
# CLOUD DEPLOYMENT
# =============================================================================

## Google Cloud Run
gcloud run deploy ai-teacher-tts \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

## AWS Lambda (with API Gateway)
# Use Zappa to deploy FastAPI to Lambda
pip install zappa
zappa init
zappa deploy production

## Heroku Deployment
# 1. Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Deploy
git push heroku main

## Azure App Service
# Configure in web.config or use App Service settings
# Set Python version to 3.9
# Set startup command: python main.py


# =============================================================================
# NGINX CONFIGURATION (Reverse Proxy)
# =============================================================================

upstream tts_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://tts_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /path/to/static/;
        expires 30d;
    }

    # Let's Encrypt SSL
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}


# =============================================================================
# LOAD BALANCING & SCALING
# =============================================================================

## Multiple workers (Gunicorn)
gunicorn main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --timeout 120

## Using HAProxy for load balancing
global
    maxconn 4096

defaults
    mode http
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend frontend
    bind *:80
    default_backend backend

backend backend
    balance roundrobin
    server backend1 127.0.0.1:8001
    server backend2 127.0.0.1:8002
    server backend3 127.0.0.1:8003


# =============================================================================
# MONITORING & LOGGING
# =============================================================================

## Prometheus metrics endpoint
# Add to main.py:
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import REGISTRY

synthesis_counter = Counter('tts_synthesis_total', 'Total synthesis requests')
synthesis_duration = Histogram('tts_synthesis_seconds', 'Synthesis duration')

@app.get("/metrics")
async def metrics():
    return generate_latest(REGISTRY)

## Log aggregation (ELK Stack or similar)
# Centralize logs for easier debugging and monitoring

## Health checks
curl http://localhost:8000/health
curl http://localhost:8000/docs


# =============================================================================
# SECURITY HARDENING
# =============================================================================

## Environment variables setup
export GOOGLE_CREDENTIALS_PATH=/secure/path/to/config.json
export API_PORT=8000
export DEBUG=False

## Use systemd user services (non-root)
[Service]
User=appuser
Group=appuser
ProtectSystem=strict
ProtectHome=yes
NoNewPrivileges=yes

## SSL/TLS Configuration
# Use self-signed certificates for testing
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use Let's Encrypt in production
certbot certonly --standalone -d your-domain.com

## Firewall
# Only allow necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable


# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

## uvicorn settings
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --http httptools

## Connection pooling
# Already configured in main.py with connection timeouts

## Caching headers
# Add cache control headers in FastAPI responses

## Database connection pooling
# For future database integration


# =============================================================================
# BACKUP & DISASTER RECOVERY
# =============================================================================

## Backup credentials
cp config.json config.json.backup
chmod 600 config.json.backup

## Version control
git tag v1.0.0 production-release

## Database backups (if using)
pg_dump -h localhost -U user database > backup.sql


# =============================================================================
# TROUBLESHOOTING
# =============================================================================

## Check if port is in use
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

## Check service status
systemctl status ai-teacher-tts

## View logs
tail -f /var/log/syslog | grep ai-teacher-tts
journalctl -u ai-teacher-tts -f

## Test connectivity
curl http://localhost:8000/health
curl http://localhost:8000/docs


# =============================================================================
# MAINTENANCE TASKS
# =============================================================================

## Update dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

## Database migrations
# For future database setup

## SSL certificate renewal
certbot renew --dry-run
certbot renew

## Restart services
systemctl restart ai-teacher-tts

## Clear cache
# If caching is implemented

## Backup and logs rotation
logrotate /etc/logrotate.d/ai-teacher-tts
