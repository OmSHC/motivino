# SSL Setup Guide for winmind.in

## Overview
This guide helps you set up SSL certificates for your winmind.in domain to enable HTTPS support.

## Prerequisites
- Domain name `winmind.in` pointing to your server IP
- Administrative access to your server
- Certbot installed (for Let's Encrypt certificates)

## Quick Setup with Let's Encrypt (Recommended)

### 1. Install Certbot
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot
```

### 2. Run the SSL Certificate Script
```bash
# Make sure you're in the project directory
cd /Users/omprakash/Ishika

# Run the certificate script
sudo ./get_ssl_cert.sh
```

### 3. Update Email Address (Optional)
Edit `get_ssl_cert.sh` and change the EMAIL variable to your actual email address before running.

### 4. Deploy with SSL
```bash
# Deploy using production compose file
docker-compose -f docker-compose.prod.yml up -d

# Or deploy with your existing deployment script
./deploy.sh
```

## Manual SSL Certificate Setup

If you prefer to use certificates from another provider:

### 1. Obtain Certificates
- Get SSL certificates from your preferred Certificate Authority
- You need two files:
  - `fullchain.pem` (certificate chain)
  - `privkey.pem` (private key)

### 2. Place Certificates
```bash
# Create ssl directory if it doesn't exist
mkdir -p ssl

# Copy your certificates
cp /path/to/your/fullchain.pem ssl/
cp /path/to/your/privkey.pem ssl/

# Set proper permissions
chmod 644 ssl/fullchain.pem
chmod 600 ssl/privkey.pem
```

### 3. Deploy
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## What Was Changed

### nginx.conf
- Added SSL configuration with TLS 1.2/1.3 support
- Added HTTP to HTTPS redirect (port 80 → 443)
- Added HTTPS server block with SSL certificates
- Updated server_name to `winmind.in www.winmind.in`

### docker-compose.prod.yml
- Added SSL certificate volume mounts
- Exposed port 443 for HTTPS traffic

## Testing SSL Setup

### 1. Check Certificate
```bash
# Test SSL certificate
openssl s_client -connect winmind.in:443 -servername winmind.in

# Or use online SSL checkers like:
# https://www.sslshopper.com/ssl-checker.html
```

### 2. Test HTTP Redirect
```bash
# Should redirect to HTTPS
curl -I http://winmind.in
```

### 3. Test HTTPS
```bash
# Should work with valid certificate
curl -I https://winmind.in
```

## Certificate Renewal

### Let's Encrypt Auto-Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Set up cron job for automatic renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual Renewal
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Renew certificate
sudo certbot certonly --standalone -d winmind.in -d www.winmind.in

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/winmind.in/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/winmind.in/privkey.pem ssl/

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues

1. **Certificate not found error**
   - Ensure certificate files exist in `./ssl/` directory
   - Check file permissions: `fullchain.pem` should be 644, `privkey.pem` should be 600

2. **Port 443 not accessible**
   - Check if port 443 is open in firewall
   - Ensure Docker container is exposing port 443

3. **HTTP not redirecting to HTTPS**
   - Check nginx configuration syntax: `nginx -t`
   - Verify domain DNS points to correct server

4. **SSL certificate errors**
   - Verify certificate validity: `openssl x509 -in ssl/fullchain.pem -text -noout`
   - Check certificate expiration date

### Logs
```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Check certificate renewal logs
sudo journalctl -u certbot
```

## Security Notes

- SSL certificates are stored in `./ssl/` directory
- Private key (`privkey.pem`) has restricted permissions (600)
- Consider using a secrets management system for production
- Regularly update nginx and SSL configurations for security patches
