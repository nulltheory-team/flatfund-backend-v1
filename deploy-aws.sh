#!/bin/bash

# AWS EC2 Deployment Script for FlatFund Backend
# This script sets up Docker and deploys the FastAPI application

set -e

echo "🚀 FlatFund Backend Deployment Script"
echo "======================================"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Install additional tools
echo "🛠️ Installing additional tools..."
sudo apt-get install -y git htop nginx certbot python3-certbot-nginx

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/flatfund
sudo chown $USER:$USER /opt/flatfund
cd /opt/flatfund

# Clone or copy application (you'll need to modify this)
echo "📥 Application deployment..."
echo "ℹ️  You need to upload your application files to /opt/flatfund"
echo "   You can use scp, git clone, or any other method"

# Create environment file
echo "🔐 Creating environment configuration..."
cat > .env << EOF
USE_LOCAL_DB=false
DATABASE_URL=postgresql://postgres:yvnreddy2002@flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com:5432/postgres
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=*
EOF

# Set up systemd service for auto-start
echo "⚙️ Setting up systemd service..."
sudo tee /etc/systemd/system/flatfund.service > /dev/null << EOF
[Unit]
Description=FlatFund Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/flatfund
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/flatfund > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Documentation
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /redoc {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files and admin UI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/flatfund /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 8000
sudo ufw --force enable

# Enable and start services
echo "🔧 Enabling services..."
sudo systemctl enable docker
sudo systemctl enable nginx
sudo systemctl enable flatfund
sudo systemctl start docker
sudo systemctl start nginx

# Display final information
echo ""
echo "✅ Deployment script completed!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Upload your application files to /opt/flatfund"
echo "2. Run: cd /opt/flatfund && sudo systemctl start flatfund"
echo "3. Check status: sudo systemctl status flatfund"
echo "4. View logs: sudo docker-compose logs -f"
echo ""
echo "🌐 Access your application:"
echo "   - API: http://$(curl -s ifconfig.me)/api/v1/apartments/"
echo "   - Docs: http://$(curl -s ifconfig.me)/docs"
echo "   - Admin UI: http://$(curl -s ifconfig.me)/static/admin.html"
echo ""
echo "🔐 To enable HTTPS:"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "📊 Useful commands:"
echo "   - Check app status: sudo systemctl status flatfund"
echo "   - View app logs: cd /opt/flatfund && sudo docker-compose logs -f"
echo "   - Restart app: sudo systemctl restart flatfund"
echo "   - Check nginx: sudo systemctl status nginx"
echo ""
