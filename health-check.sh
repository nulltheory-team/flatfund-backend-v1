#!/bin/bash

# Health check script for deployed application

echo "🏥 FlatFund Backend Health Check"
echo "==============================="

# Check if running on EC2 or locally
if [ -f "/opt/flatfund/docker-compose.yml" ]; then
    echo "🌩️  Running on AWS EC2"
    BASE_URL="http://localhost"
    cd /opt/flatfund
else
    echo "💻 Running locally"
    BASE_URL="http://localhost:8000"
fi

echo ""
echo "🔍 System Status:"
echo "=================="

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker: Not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose: $(docker-compose --version)"
else
    echo "❌ Docker Compose: Not installed"
fi

# Check if on EC2
if [ -f "/opt/flatfund/docker-compose.yml" ]; then
    echo ""
    echo "🐳 Docker Services:"
    echo "=================="
    sudo docker-compose ps
    
    echo ""
    echo "⚙️  System Services:"
    echo "==================="
    sudo systemctl status flatfund --no-pager -l
    sudo systemctl status nginx --no-pager -l
fi

echo ""
echo "🌐 Application Health:"
echo "====================="

# Test API endpoints
endpoints=(
    "$BASE_URL/docs"
    "$BASE_URL/api/v1/apartments/"
    "$BASE_URL/static/admin.html"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testing $endpoint ... "
    if curl -s -f "$endpoint" > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ Failed"
    fi
done

echo ""
echo "📊 Resource Usage:"
echo "=================="
echo "Memory:"
free -h
echo ""
echo "Disk:"
df -h /
echo ""

if command -v docker &> /dev/null; then
    echo "Docker containers:"
    sudo docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
fi

echo ""
echo "📋 Quick Commands:"
echo "=================="
if [ -f "/opt/flatfund/docker-compose.yml" ]; then
    echo "View logs:     cd /opt/flatfund && sudo docker-compose logs -f"
    echo "Restart app:   sudo systemctl restart flatfund"
    echo "Check status:  sudo systemctl status flatfund"
else
    echo "Start local:   docker-compose up --build"
    echo "View logs:     docker-compose logs -f"
fi

echo ""
echo "🎯 Access URLs:"
echo "=============="
if [ -f "/opt/flatfund/docker-compose.yml" ]; then
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-ec2-ip")
    echo "Admin UI:  http://$PUBLIC_IP/static/admin.html"
    echo "API Docs:  http://$PUBLIC_IP/docs"
    echo "API:       http://$PUBLIC_IP/api/v1/apartments/"
else
    echo "Admin UI:  http://localhost:8000/static/admin.html"
    echo "API Docs:  http://localhost:8000/docs"
    echo "API:       http://localhost:8000/api/v1/apartments/"
fi
