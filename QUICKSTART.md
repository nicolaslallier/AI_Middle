# Quick Start Guide

Get the Python middleware up and running in 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- Git installed
- (Optional) Python 3.11+ and Poetry for local development

## Start Everything with Docker

### 1. Clone and Navigate
```bash
cd /Users/nicolaslallier/Dev\ Nick/AI_Middle
```

### 2. Start All Services
```bash
docker-compose up -d
```

This starts:
- ✅ Auth Service (OAuth2) on port 8001
- ✅ Gateway Service (API Gateway) on port 8002  
- ✅ Aggregation Service (Data) on port 8003
- ✅ PostgreSQL databases (3 instances)
- ✅ Redis cache

### 3. Verify Services are Running
```bash
# Check all containers
docker-compose ps

# Check health endpoints
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### 4. View API Documentation
Open in your browser:
- Auth Service: http://localhost:8001/docs
- Gateway Service: http://localhost:8002/docs
- Aggregation Service: http://localhost:8003/docs

## Try It Out

### Register a User
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Response includes `access_token` and `refresh_token`.

### Use Access Token
```bash
# Save token from login response
TOKEN="your-access-token-here"

# Make authenticated request through gateway
curl http://localhost:8002/api/data/aggregate \
  -H "Authorization: Bearer $TOKEN"
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
docker-compose logs -f gateway-service
docker-compose logs -f aggregation-service
```

## Stop Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (keeps data volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Development Mode (Hot Reload)

Code changes automatically reload in Docker:

```bash
# Edit any Python file in services/*/src/
# Service automatically reloads
docker-compose logs -f auth-service
# Watch for "Application startup complete" message
```

## Local Development (without Docker)

### Setup Auth Service Locally

```bash
cd services/auth-service

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Start local PostgreSQL and Redis (or use Docker for just databases)
docker-compose up -d auth-db redis

# Run migrations
poetry run alembic upgrade head

# Start service
poetry run python -m src.infrastructure.api.main
```

### Run Tests

```bash
cd services/auth-service

# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html

# Specific test
poetry run pytest tests/unit/test_email_value_object.py -v
```

### Code Quality Checks

```bash
cd services/auth-service

# Format code
poetry run black src/

# Lint
poetry run ruff check src/

# Type check
poetry run mypy src/

# Security check
poetry run bandit -r src/
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8001, 8002, or 8003
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Stop the conflicting process or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Restart database containers
docker-compose restart auth-db gateway-db aggregation-db

# Check database logs
docker-compose logs auth-db
```

### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker-compose up -d

# Wait for services to be healthy
sleep 10
curl http://localhost:8001/health
```

### View Metrics
```bash
# Prometheus metrics
curl http://localhost:8001/metrics
curl http://localhost:8002/metrics
curl http://localhost:8003/metrics
```

## Next Steps

1. **Read Architecture**: See `docs/ARCHITECTURE.md`
2. **Review ADRs**: See `docs/ADR-*.md`
3. **Read Main README**: See `README.md`
4. **Review Code Standards**: See `.cursorrules`
5. **Write Your First Feature**: Follow TDD approach in docs

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart auth-service

# Run command in container
docker-compose exec auth-service poetry run pytest

# Scale service
docker-compose up -d --scale auth-service=3

# Stop services
docker-compose down
```

## IDE Setup

### VS Code / Cursor

1. Install Python extension
2. Select Poetry environment: Cmd+Shift+P → "Python: Select Interpreter"
3. Install recommended extensions (will prompt automatically)

### PyCharm

1. Configure Poetry as project interpreter
2. Mark `src/` as Sources Root
3. Mark `tests/` as Test Sources Root
4. Enable pytest as test runner

## Getting Help

- Check logs: `docker-compose logs -f [service-name]`
- Check health: `curl http://localhost:800X/health`
- Review documentation in `docs/` folder
- Check `.cursorrules` for coding standards

---

**Happy coding! 🚀**

