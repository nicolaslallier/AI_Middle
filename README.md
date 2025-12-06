# AI Middle - Python Middleware Application

A production-ready Python middleware application following **Clean Architecture** and **SOLID principles**, implementing OAuth2 authentication, API gateway, and data aggregation services.

## Architecture Overview

This project implements a microservices architecture divided by technical layers:

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                  (Web / Mobile / Multiple)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gateway Service                           │
│        (Rate Limiting, Circuit Breaker, Routing)            │
└──────────┬─────────────────────────┬────────────────────────┘
           │                         │
           ▼                         ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│   Auth Service       │   │   Aggregation Service            │
│  (OAuth2, JWT)       │   │  (Data aggregation, transform)   │
└──────────────────────┘   └──────────────────────────────────┘
           │                         │
           ▼                         ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│   PostgreSQL (Auth)  │   │   PostgreSQL (Aggregation)       │
└──────────────────────┘   └──────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Redis (Shared) │
              │ Cache, Sessions │
              └────────────────┘
```

## Core Principles

### Clean Architecture (Uncle Bob)

Each service follows strict Clean Architecture layers:

1. **Domain** (Entities, Value Objects) - Pure business logic, no external dependencies
2. **Application** (Use Cases, Ports) - Business workflows, defines interfaces
3. **Adapters** (Controllers, Repositories, DTOs) - Implements ports, converts data
4. **Infrastructure** (FastAPI, Database, External Services) - Framework and tools

**Dependency Rule**: Dependencies point inward only. Inner layers know nothing about outer layers.

### SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Extension through interfaces, not modification
- **Liskov Substitution**: Proper interface contracts with ABC
- **Interface Segregation**: Small, focused protocols
- **Dependency Inversion**: All dependencies through abstractions

## Technology Stack

### Core Technologies
- **Python 3.11+**: Latest stable Python
- **FastAPI**: Modern async web framework with auto-documentation
- **Pydantic v2**: Data validation and settings
- **SQLAlchemy 2.0**: Async ORM
- **PostgreSQL**: Relational database (one per service)
- **Redis**: Caching, sessions, rate limiting

### Testing
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage (>80% required)
- **Faker**: Test data generation
- **TestContainers**: Real databases in integration tests

### Code Quality
- **Black**: Code formatting (line length 100)
- **Ruff**: Fast linting and import sorting
- **mypy**: Strict type checking
- **pre-commit**: Automated quality checks
- **bandit**: Security linting

### Observability
- **structlog**: Structured JSON logging
- **Prometheus**: Metrics collection
- **OpenTelemetry**: Distributed tracing
- **Health checks**: Liveness and readiness probes

## Project Structure

```
AI_Middle/
├── services/
│   ├── auth-service/              # OAuth2 Authentication
│   │   ├── src/
│   │   │   ├── domain/           # Entities, value objects, exceptions
│   │   │   ├── application/      # Use cases, ports (interfaces)
│   │   │   ├── adapters/         # Controllers, repositories, DTOs
│   │   │   └── infrastructure/   # FastAPI, database, JWT, DI
│   │   ├── tests/                # Unit, integration, e2e tests
│   │   ├── alembic/              # Database migrations
│   │   ├── pyproject.toml        # Dependencies
│   │   └── Dockerfile            # Container definition
│   │
│   ├── gateway-service/           # API Gateway
│   │   ├── src/
│   │   │   └── infrastructure/
│   │   │       ├── middleware/   # Rate limiting, circuit breaker
│   │   │       └── api/          # FastAPI routes
│   │   └── ...
│   │
│   └── aggregation-service/       # Data Aggregation
│       ├── src/
│       │   └── infrastructure/
│       │       └── api/          # Aggregation endpoints
│       └── ...
│
├── shared/
│   └── common/                    # Shared library
│       ├── domain/               # Base entity, value object
│       ├── exceptions.py         # Common exception hierarchy
│       ├── result.py             # Result monad for error handling
│       ├── logging.py            # Structured logging setup
│       ├── metrics.py            # Prometheus metrics
│       └── tracing.py            # OpenTelemetry tracing
│
├── docker-compose.yml            # All services + databases
├── .pre-commit-config.yaml       # Quality checks
├── .cursorrules                  # Development standards
└── README.md                     # This file
```

## Getting Started

### Prerequisites

- **Docker & Docker Compose**: For running all services
- **Python 3.11+**: For local development
- **Poetry**: Python dependency management

### Quick Start

1. **Clone the repository**
```bash
cd AI_Middle
```

2. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

This starts:
- Auth Service on port 8001
- Gateway Service on port 8002
- Aggregation Service on port 8003
- PostgreSQL databases (3 instances)
- Redis (shared)

3. **Verify services are running**
```bash
# Check health
curl http://localhost:8001/health  # Auth service
curl http://localhost:8002/health  # Gateway service
curl http://localhost:8003/health  # Aggregation service

# Access API docs
open http://localhost:8001/docs  # Auth service Swagger UI
open http://localhost:8002/docs  # Gateway service Swagger UI
open http://localhost:8003/docs  # Aggregation service Swagger UI
```

### Local Development (without Docker)

1. **Install dependencies for auth service**
```bash
cd services/auth-service
poetry install
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run database migrations**
```bash
poetry run alembic upgrade head
```

4. **Run the service**
```bash
poetry run python -m src.infrastructure.api.main
```

5. **Run tests**
```bash
# All tests with coverage
poetry run pytest

# Unit tests only (fast)
poetry run pytest tests/unit/

# With coverage report
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Running with Hot Reload

For development with hot reload:

```bash
docker-compose up
# Or for a specific service:
docker-compose up auth-service
```

Code changes are automatically reloaded thanks to volume mounts.

## Service Details

### Auth Service (Port 8001)

**OAuth2 authentication and authorization service**

Key endpoints:
- `POST /auth/register` - Register new user
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/refresh` - Refresh access token

Features:
- JWT access and refresh tokens
- bcrypt password hashing
- Email verification
- User roles
- Account status management

### Gateway Service (Port 8002)

**API gateway with rate limiting and circuit breaker**

Features:
- Routes requests to backend services
- Redis-based rate limiting (60 req/min default)
- Circuit breaker pattern (prevents cascading failures)
- Request/response logging
- Metrics collection

Routes:
- `/auth/*` → Auth Service
- `/api/*` → Aggregation Service

### Aggregation Service (Port 8003)

**Data aggregation and transformation**

Key endpoints:
- `GET /data/aggregate` - Aggregate data from multiple sources
- `POST /data/transform` - Transform data with business rules

Features:
- Multi-source data aggregation
- Business logic orchestration
- Response caching
- Data transformation

## Testing Strategy

We follow Test-Driven Development (TDD) with comprehensive test coverage:

### Test Layers

1. **Unit Tests** (Domain & Application layers)
   - Fast, no I/O
   - Mock all external dependencies
   - Test business logic in isolation
   - Target: 100% coverage for domain, 95% for application

2. **Integration Tests** (Adapters layer)
   - Test with real databases (TestContainers)
   - Test repository implementations
   - Target: 85% coverage

3. **E2E Tests** (Infrastructure layer)
   - Full API tests
   - Test complete user flows
   - Target: 70% coverage

### Running Tests

```bash
# All tests with coverage
poetry run pytest

# Specific test file
poetry run pytest tests/unit/test_email_value_object.py

# With verbose output
poetry run pytest -v

# Stop on first failure
poetry run pytest -x

# Run tests matching pattern
poetry run pytest -k "test_email"
```

## Code Quality

### Pre-commit Hooks

Install hooks:
```bash
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```

Hooks include:
1. Black formatting
2. Ruff linting
3. mypy type checking
4. pytest unit tests
5. Secret detection

### Manual Quality Checks

```bash
# Format code
poetry run black src/

# Lint code
poetry run ruff check src/

# Type check
poetry run mypy src/

# Security check
poetry run bandit -r src/
```

## API Documentation

Each service provides auto-generated OpenAPI documentation:

- Auth Service: http://localhost:8001/docs
- Gateway Service: http://localhost:8002/docs
- Aggregation Service: http://localhost:8003/docs

ReDoc alternative:
- Auth Service: http://localhost:8001/redoc

## Monitoring & Observability

### Prometheus Metrics

Metrics endpoint for each service:
- http://localhost:8001/metrics
- http://localhost:8002/metrics
- http://localhost:8003/metrics

Available metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `database_query_duration_seconds` - DB query performance
- `cache_operations_total` - Cache hit/miss rates
- `business_operations_total` - Business operation counts

### Health Checks

Each service provides:
- `/health` - Basic liveness check
- `/health/ready` - Readiness check (includes DB connectivity)

### Structured Logging

All services use structured JSON logging:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "event": "user_registered",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com"
}
```

## Development Workflow

1. **Create feature branch**
```bash
git checkout -b feature/my-feature
```

2. **Write test first** (TDD)
```python
# tests/unit/test_my_feature.py
def test_my_feature():
    # Arrange
    # Act
    # Assert
    pass
```

3. **Implement feature**
```python
# src/domain/...
# Follow Clean Architecture layers
```

4. **Run quality checks**
```bash
poetry run pytest
poetry run mypy src/
poetry run ruff check src/
```

5. **Commit with pre-commit hooks**
```bash
git add .
git commit -m "feat: add my feature"
```

6. **Push and create PR**

## Environment Variables

### Auth Service

```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=auth_db
DATABASE_USER=auth_user
DATABASE_PASSWORD=auth_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Gateway Service

```bash
# Backend Services
AUTH_SERVICE_URL=http://localhost:8001
AGGREGATION_SERVICE_URL=http://localhost:8003

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
CIRCUIT_BREAKER_THRESHOLD=5
```

## Deployment

### Docker Production Build

```bash
# Build images
docker-compose build

# Run in production mode
docker-compose -f docker-compose.yml up -d
```

### Kubernetes (Future)

Helm charts and K8s manifests to be added for:
- Horizontal pod autoscaling
- Service mesh integration
- Secret management
- Ingress configuration

## Contributing

1. Follow the coding standards in `.cursorrules`
2. Write tests first (TDD)
3. Maintain test coverage above 80%
4. Use type hints everywhere
5. Write docstrings for public APIs
6. Run pre-commit hooks before committing

## License

Proprietary - AI Middle Team

## Support

For questions or issues, contact the development team.

---

**Built with ❤️ following Clean Architecture and SOLID principles**

