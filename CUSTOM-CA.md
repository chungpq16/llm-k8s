# Adding Custom Root CA Certificates

## Overview
This guide shows how to add custom root CA certificates to both the frontend and backend Docker containers.

## Steps

### 1. Place Your CA Certificate

Put your root CA certificate file in the project root directory:
```bash
# Example: Copy your CA cert to the project
cp /path/to/your/custom-ca.crt ./custom-ca.crt
```

### 2. Update Dockerfiles

#### Frontend (Dockerfile)
Uncomment these lines in `Dockerfile`:
```dockerfile
# Copy custom CA certificate (optional)
COPY custom-ca.crt /usr/local/share/ca-certificates/custom-ca.crt
RUN update-ca-certificates
```

#### Backend (agent/Dockerfile)
Uncomment these lines in `agent/Dockerfile`:
```dockerfile
# Copy custom CA certificate (optional)
COPY custom-ca.crt /usr/local/share/ca-certificates/custom-ca.crt
RUN update-ca-certificates
```

### 3. Update .dockerignore

Make sure your CA certificate is NOT ignored. Edit `.dockerignore` to allow it:
```bash
# Add this line to .dockerignore to explicitly include it
!custom-ca.crt
```

### 4. Build with Custom CA

```bash
# Rebuild the images
docker-compose build

# Or build individually
docker build -t chat-k8s-frontend .
docker build -t chat-k8s-agent ./agent
```

## Multiple CA Certificates

If you have multiple CA certificates:

### Option 1: Single Combined File
```bash
# Combine multiple certs into one file
cat ca1.crt ca2.crt ca3.crt > custom-ca.crt
```

### Option 2: Multiple Files
Update Dockerfiles to copy all certs:
```dockerfile
# Frontend/Backend Dockerfile
COPY ca1.crt /usr/local/share/ca-certificates/ca1.crt
COPY ca2.crt /usr/local/share/ca-certificates/ca2.crt
COPY ca3.crt /usr/local/share/ca-certificates/ca3.crt
RUN update-ca-certificates
```

## Environment-Specific CA Certificates

For different environments, use build arguments:

### 1. Update Dockerfile
```dockerfile
# Add build argument
ARG CA_CERT_FILE=custom-ca.crt

# Copy based on argument
COPY ${CA_CERT_FILE} /usr/local/share/ca-certificates/custom-ca.crt
RUN update-ca-certificates
```

### 2. Build with Argument
```bash
# Development
docker build --build-arg CA_CERT_FILE=dev-ca.crt -t app:dev .

# Production
docker build --build-arg CA_CERT_FILE=prod-ca.crt -t app:prod .
```

## Docker Compose with CA

Update `docker-compose.yml` to use build args:

```yaml
services:
  agent:
    build:
      context: ./agent
      dockerfile: Dockerfile
      args:
        CA_CERT_FILE: ${CA_CERT_FILE:-custom-ca.crt}
    # ... rest of config

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        CA_CERT_FILE: ${CA_CERT_FILE:-custom-ca.crt}
    # ... rest of config
```

Then set in `.env`:
```bash
CA_CERT_FILE=custom-ca.crt
```

## Verification

### Verify CA is Installed

#### Frontend (Alpine)
```bash
docker exec -it chat-k8s-frontend ls -la /usr/local/share/ca-certificates/
docker exec -it chat-k8s-frontend cat /etc/ssl/certs/ca-certificates.crt | grep -A5 "custom"
```

#### Backend (Debian)
```bash
docker exec -it chat-k8s-agent ls -la /usr/local/share/ca-certificates/
docker exec -it chat-k8s-agent cat /etc/ssl/certs/ca-certificates.crt | grep -A5 "custom"
```

### Test HTTPS Connection
```bash
# Test from inside container
docker exec -it chat-k8s-agent curl -v https://your-internal-service.com

# Should show successful SSL handshake
```

## Python-Specific CA Configuration

If Python needs additional CA configuration:

```dockerfile
# In agent/Dockerfile, add:
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## Node.js-Specific CA Configuration

If Node.js needs additional CA configuration:

```dockerfile
# In Dockerfile, add:
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
```

## Troubleshooting

### Issue: Certificate Not Trusted
```bash
# Check if cert was properly added
docker run --rm -it chat-k8s-agent bash
ls -la /usr/local/share/ca-certificates/
cat /etc/ssl/certs/ca-certificates.crt | grep -c "BEGIN CERTIFICATE"
```

### Issue: Python SSL Errors
Add to agent code or environment:
```python
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
```

### Issue: Node.js SSL Errors
```bash
# Temporarily disable SSL verification (NOT for production)
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

## Security Notes

1. **Never commit private keys** - only copy public certificates (`.crt` files)
2. **Verify certificate source** - ensure CA certificates are from trusted sources
3. **Update regularly** - keep CA certificates up to date
4. **Use secrets in production** - mount certificates as Docker secrets instead of building them into images:

```yaml
# docker-compose.yml with secrets
services:
  agent:
    secrets:
      - ca_cert
    # ... rest of config

secrets:
  ca_cert:
    file: ./custom-ca.crt
```

Then in Dockerfile:
```dockerfile
# Use secret at runtime
RUN --mount=type=secret,id=ca_cert \
    cp /run/secrets/ca_cert /usr/local/share/ca-certificates/custom-ca.crt && \
    update-ca-certificates
```
