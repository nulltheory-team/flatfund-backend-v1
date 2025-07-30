# 🚀 FlatFund Backend - Complete AWS Deployment Guide

## 📋 **Overview**
This guide will help you deploy your FlatFund FastAPI backend to AWS EC2 with Docker, including the admin UI and RDS database connectivity.

## 🎯 **What You'll Get**
- ✅ Dockerized FastAPI application
- ✅ Admin UI accessible via web browser
- ✅ RDS PostgreSQL database integration
- ✅ Nginx reverse proxy with SSL support
- ✅ Auto-restart on server reboot
- ✅ Free tier compatible (t2.micro)

## 🔧 **Prerequisites**

### AWS Account Setup
1. **AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **AWS CLI** (optional): For easier management

### Local Requirements
- SSH client (Terminal on Mac/Linux, PuTTY on Windows)
- Your application files (this directory)

## 🚀 **Step-by-Step Deployment**

### **Step 1: Launch EC2 Instance**

1. **Go to EC2 Console**
   - Navigate to: AWS Console → EC2 → Launch Instance

2. **Configure Instance**
   - **Name**: `flatfund-backend`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: `t2.micro` (Free tier)
   - **Key Pair**: Create new or use existing
   - **Security Group**: Create new with these rules:
     ```
     SSH (22)     - Your IP only
     HTTP (80)    - Anywhere (0.0.0.0/0)
     HTTPS (443)  - Anywhere (0.0.0.0/0)
     Custom (8000)- Anywhere (0.0.0.0/0) [for testing]
     ```

3. **Launch Instance**
   - Note down the **Public IP address**

### **Step 2: Connect to Your Instance**

```bash
# Replace with your key file and EC2 public IP
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### **Step 3: Upload Application Files**

From your local machine (new terminal):

```bash
# Package the application
cd /Users/ysandeepkumarreddy/flatfund-backend-v1
./package-for-deployment.sh

# Upload to EC2 (replace with your details)
scp -i "your-key.pem" /tmp/flatfund-backend-*.tar.gz ubuntu@your-ec2-ip:/home/ubuntu/

# Extract on EC2
ssh -i "your-key.pem" ubuntu@your-ec2-ip
tar -xzf flatfund-backend-*.tar.gz
cd flatfund-backend-*
```

### **Step 4: Run Deployment Script**

On your EC2 instance:

```bash
# Make executable and run
chmod +x deploy-aws.sh
./deploy-aws.sh

# Wait for completion (5-10 minutes)
```

### **Step 5: Deploy Application**

```bash
# Copy files to deployment directory
sudo cp -r * /opt/flatfund/

# Navigate to deployment directory
cd /opt/flatfund

# Configure environment (edit database URL if needed)
sudo nano .env

# Start the application
sudo systemctl start flatfund

# Check status
sudo systemctl status flatfund
```

### **Step 6: Test Your Deployment**

Replace `your-ec2-ip` with your actual EC2 public IP:

- **🏠 Admin UI**: `http://your-ec2-ip/static/admin.html`
- **📚 API Docs**: `http://your-ec2-ip/docs`
- **🔗 API Endpoint**: `http://your-ec2-ip/api/v1/apartments/`

## 🌐 **Access URLs**

After successful deployment, you'll have:

```
🏢 Admin Dashboard: http://your-ec2-ip/static/admin.html
📖 API Documentation: http://your-ec2-ip/docs
🔄 Health Check: http://your-ec2-ip/api/v1/apartments/
```

## 🔐 **Security & Production Setup**

### **Optional: Set Up Domain & HTTPS**

1. **Point domain to EC2**:
   - Create A record: `api.yourdomain.com` → `your-ec2-ip`

2. **Install SSL certificate**:
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```

3. **Update security group**:
   - Remove port 8000 access
   - Keep only 22, 80, 443

### **Environment Security**

Edit `/opt/flatfund/.env`:
```bash
sudo nano /opt/flatfund/.env
```

Update:
- `SECRET_KEY` - Generate new random key
- `CORS_ORIGINS` - Restrict to your domain
- `DATABASE_URL` - Verify RDS credentials

## 📊 **Monitoring & Maintenance**

### **Check Application Status**
```bash
# Service status
sudo systemctl status flatfund

# Application logs
cd /opt/flatfund && sudo docker-compose logs -f

# System resources
htop
```

### **Common Operations**
```bash
# Restart application
sudo systemctl restart flatfund

# Update application
cd /opt/flatfund
sudo docker-compose pull
sudo docker-compose up -d --build

# View real-time logs
sudo docker-compose logs -f
```

## 🚨 **Troubleshooting**

### **Application Won't Start**
```bash
# Check Docker status
sudo systemctl status docker

# Check logs
sudo docker-compose logs

# Manual start
sudo docker-compose up --build
```

### **Can't Access from Browser**
1. Check EC2 security group allows port 80/443
2. Verify nginx is running: `sudo systemctl status nginx`
3. Check if port is open: `sudo netstat -tulpn | grep :80`

### **Database Connection Issues**
```bash
# Test RDS connectivity
python3 init_rds.py

# Check environment variables
cat .env
```

## 💰 **Cost Optimization**

- **EC2**: t2.micro (free tier) = $0/month for first year
- **RDS**: Already configured
- **Data Transfer**: Minimal for development
- **Storage**: EBS 8GB free tier

**Estimated Monthly Cost**: $0-5 (free tier)

## 🎉 **Success!**

Your FlatFund backend is now live! You can:

- ✅ Access the admin UI via browser
- ✅ Use the REST API from any client
- ✅ Connect mobile/web frontends
- ✅ Scale as needed

**Public URLs** (replace with your EC2 IP):
- Admin UI: `http://your-ec2-ip/static/admin.html`
- API: `http://your-ec2-ip/api/v1/apartments/`
- Docs: `http://your-ec2-ip/docs`
