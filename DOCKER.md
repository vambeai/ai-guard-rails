# Docker Deployment Guide

This guide explains how to deploy the FastAPI Guardrails Validator service using Docker.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

**Production:**

```bash
docker-compose up -d
```

**Development (with hot reload):**

```bash
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Using Docker Commands

**Build the image:**

```bash
docker build -t guardrails-validator:latest .
```

**Run the container:**

```bash
docker run -d -p 8000:8000 --name guardrails-api guardrails-validator:latest
```

## Docker Files Overview

### Production Files

- **`Dockerfile`** - Production-optimized image

  - Uses Python 3.11 slim
  - Multi-layer caching for faster builds
  - Runs as non-root user for security
  - Includes health checks

- **`docker-compose.yml`** - Production deployment
  - Single service configuration
  - Port mapping
  - Health checks
  - Restart policies

### Development Files

- **`Dockerfile.dev`** - Development image

  - Includes all development tools
  - Auto-reload enabled

- **`docker-compose.dev.yml`** - Development environment

  - Volume mounting for hot reload
  - Easy debugging

- **`.dockerignore`** - Build optimization
  - Excludes unnecessary files from Docker context

## Detailed Usage

### Production Deployment

#### 1. Build and Start

```bash
# Build and start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 2. Test the Service

```bash
# Health check
curl http://localhost:8000/health

# Test validation endpoint
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Call me at 123-456-7890",
    "guardrails": [
      {
        "name": "RegexMatch",
        "config": {
          "regex": "\\d{3}-\\d{3}-\\d{4}"
        }
      }
    ]
  }'
```

#### 3. Stop the Service

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Development Deployment

#### 1. Start Development Environment

```bash
# Start with hot reload
docker-compose -f docker-compose.dev.yml up

# Or in detached mode
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. Make Changes

Any changes to files in the `app/` directory will trigger an automatic reload.

#### 3. View Logs

```bash
docker-compose -f docker-compose.dev.yml logs -f
```

#### 4. Stop Development Environment

```bash
docker-compose -f docker-compose.dev.yml down
```

## Docker Commands Reference

### Building

```bash
# Build production image
docker build -t guardrails-validator:latest .

# Build development image
docker build -f Dockerfile.dev -t guardrails-validator:dev .

# Build with no cache
docker build --no-cache -t guardrails-validator:latest .
```

### Running

```bash
# Run production container
docker run -d \
  -p 8000:8000 \
  --name guardrails-api \
  --restart unless-stopped \
  guardrails-validator:latest

# Run with custom port
docker run -d \
  -p 9000:8000 \
  --name guardrails-api \
  guardrails-validator:latest

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  --name guardrails-api \
  guardrails-validator:latest
```

### Managing Containers

```bash
# List running containers
docker ps

# View logs
docker logs guardrails-api

# Follow logs
docker logs -f guardrails-api

# Stop container
docker stop guardrails-api

# Start container
docker start guardrails-api

# Restart container
docker restart guardrails-api

# Remove container
docker rm guardrails-api

# Remove container (force)
docker rm -f guardrails-api
```

### Inspecting

```bash
# View container details
docker inspect guardrails-api

# Check health status
docker inspect --format='{{.State.Health.Status}}' guardrails-api

# Execute command in container
docker exec -it guardrails-api /bin/bash

# View resource usage
docker stats guardrails-api
```

## Environment Variables

You can customize the service using environment variables:

| Variable | Default   | Description |
| -------- | --------- | ----------- |
| `HOST`   | `0.0.0.0` | Server host |
| `PORT`   | `8000`    | Server port |

### Using Environment Variables

**In docker-compose.yml:**

```yaml
environment:
  - HOST=0.0.0.0
  - PORT=8000
```

**In docker run command:**

```bash
docker run -e HOST=0.0.0.0 -e PORT=8000 ...
```

**Using .env file:**

```bash
# Create .env file
echo "HOST=0.0.0.0" > .env
echo "PORT=8000" >> .env

# Use with docker-compose
docker-compose --env-file .env up
```

## Installing Guardrails Validators

The base image includes the Guardrails AI framework, but you need to install specific validators.

### Option 1: Build Custom Image

Create a new Dockerfile that extends the base image:

```dockerfile
FROM guardrails-validator:latest

USER root

# Install validators
RUN pip install guardrails-ai && \
    guardrails hub install hub://guardrails/regex_match && \
    guardrails hub install hub://guardrails/competitor_check && \
    guardrails hub install hub://guardrails/toxic_language

USER appuser
```

Build and run:

```bash
docker build -f Dockerfile.custom -t guardrails-validator:custom .
docker run -d -p 8000:8000 guardrails-validator:custom
```

### Option 2: Install in Running Container

```bash
# Access container shell
docker exec -it guardrails-api /bin/bash

# Inside container, switch to root
# Note: Container runs as 'appuser', may need root for installations

# Install validators
pip install <validator-package>
guardrails hub install hub://guardrails/regex_match
```

## Production Considerations

### 1. Security

- The Dockerfile uses a non-root user (`appuser`) for security
- Consider using Docker secrets for sensitive data
- Regularly update base image for security patches

### 2. Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  guardrails-api:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G
```

### 3. Logging

Configure logging drivers:

```yaml
services:
  guardrails-api:
    # ... other config ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. Health Checks

The Dockerfile includes a health check. Monitor it:

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' guardrails-api | jq
```

### 5. Reverse Proxy

Use nginx or Traefik as a reverse proxy:

**Example nginx configuration:**

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. Multiple Instances

Scale horizontally with docker-compose:

```bash
docker-compose up -d --scale guardrails-api=3
```

Or use a load balancer configuration.

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs guardrails-api

# Check if port is already in use
lsof -i :8000

# Try different port
docker run -p 9000:8000 ...
```

### Health Check Failing

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' guardrails-api

# View health check logs
docker inspect guardrails-api | jq '.[0].State.Health'

# Disable health check temporarily
docker run --no-healthcheck ...
```

### Performance Issues

```bash
# Check resource usage
docker stats guardrails-api

# Increase memory limit
docker run -m 2g ...

# Check for CPU throttling
docker stats --no-stream
```

### Connection Refused

```bash
# Check if container is running
docker ps

# Check port mapping
docker port guardrails-api

# Check network
docker network inspect bridge

# Test from inside container
docker exec guardrails-api curl http://localhost:8000/health
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t guardrails-validator:latest .

      - name: Run tests
        run: docker run guardrails-validator:latest python -m pytest

      - name: Push to registry
        run: |
          docker tag guardrails-validator:latest registry.example.com/guardrails-validator:latest
          docker push registry.example.com/guardrails-validator:latest
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Guardrails AI Documentation](https://www.guardrailsai.com/docs)
