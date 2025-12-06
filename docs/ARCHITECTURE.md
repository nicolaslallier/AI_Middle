# Architecture Documentation

## Clean Architecture Overview

This project strictly follows Uncle Bob's Clean Architecture principles. Each service is organized into four concentric layers with dependencies pointing inward only.

### Layer Descriptions

#### 1. Domain Layer (Core)
**Location**: `src/domain/`
**Dependencies**: None (pure Python)
**Purpose**: Business entities and rules

Components:
- **Entities**: Objects with identity and lifecycle (e.g., User)
- **Value Objects**: Immutable objects compared by value (e.g., Email, UserId)
- **Domain Exceptions**: Business rule violations

Rules:
- No framework dependencies
- No external library dependencies
- Pure business logic only
- 100% test coverage required

Example:
```python
@dataclass
class User(BaseEntity):
    """User entity with business rules."""

    def can_login(self) -> bool:
        """Business rule: only active users with verified emails can login."""
        return self.status == UserStatus.ACTIVE and self.email_verified
```

#### 2. Application Layer
**Location**: `src/application/`
**Dependencies**: Domain layer only
**Purpose**: Use cases and business workflows

Components:
- **Use Cases**: Application-specific business rules
- **Ports**: Interfaces (abstract base classes) for external dependencies
- **DTOs**: Data transfer between layers

Rules:
- Define interfaces (ports) for repositories and services
- Implement business workflows
- No framework knowledge
- 95% test coverage required

Example:
```python
class RegisterUser:
    """Use case for user registration."""

    def __init__(
        self,
        user_repository: IUserRepository,  # Port (interface)
        password_hasher: IPasswordHasher,  # Port (interface)
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, email: str, password: str) -> Result[User, Error]:
        """Execute registration use case."""
        # Business logic here
```

#### 3. Adapters Layer
**Location**: `src/adapters/`
**Dependencies**: Application and Domain layers
**Purpose**: Convert data between external world and application

Components:
- **Controllers**: Handle HTTP requests, delegate to use cases
- **Repositories**: Implement port interfaces for data persistence
- **Presenters**: Format responses
- **DTOs**: API request/response schemas

Rules:
- Implement interfaces defined in application layer
- No business logic (only orchestration)
- Convert between domain entities and external formats
- 85% test coverage required

Example:
```python
class UserRepository(IUserRepository):
    """PostgreSQL implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email."""
        # Database query here
        # Convert model to entity
```

#### 4. Infrastructure Layer
**Location**: `src/infrastructure/`
**Dependencies**: All other layers
**Purpose**: Frameworks, tools, and external services

Components:
- **FastAPI Application**: Web framework setup
- **Database**: SQLAlchemy models and migrations
- **External Services**: JWT, password hashing
- **Configuration**: Settings and environment variables
- **Dependency Injection**: Wire everything together

Rules:
- Framework-specific code only in this layer
- No business logic
- 70% test coverage required

## Dependency Inversion Principle

All dependencies point inward through abstractions:

```
Infrastructure → Adapters → Application → Domain
     ↓              ↓            ↓
  FastAPI      Controllers   Use Cases   Entities
  Database     Repositories   Ports      Value Objects
  JWT          DTOs          Interfaces
```

Example of dependency inversion:

```python
# Application layer defines the interface (port)
class IUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        pass

# Adapters layer implements the interface
class UserRepository(IUserRepository):
    async def find_by_email(self, email: Email) -> User | None:
        # Implementation using SQLAlchemy
        pass

# Infrastructure layer wires it up
def get_user_repository(session: AsyncSession) -> IUserRepository:
    return UserRepository(session)

# Use case depends on interface, not implementation
class RegisterUser:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository  # Depends on abstraction
```

## Result Monad Pattern

We use the Result monad for explicit error handling without exceptions:

```python
from common.result import Result, Ok, Err

def authenticate(email: str, password: str) -> Result[User, AuthError]:
    """Authenticate user."""
    user = repository.find_by_email(email)
    if not user:
        return Err(AuthError.USER_NOT_FOUND)

    if not verify_password(password, user.password_hash):
        return Err(AuthError.INVALID_PASSWORD)

    return Ok(user)

# Usage
result = authenticate("user@example.com", "password")
if result.is_ok():
    user = result.unwrap()
    print(f"Welcome {user.email}")
else:
    error = result.unwrap_err()
    print(f"Error: {error}")
```

Benefits:
- Errors are explicit in the type system
- Cannot forget to handle errors
- Functional programming style
- Composable with map, and_then, etc.

## Service Communication

### Synchronous (HTTP)

Gateway service communicates with backend services via HTTP:

```python
# Gateway service
async with httpx.AsyncClient() as client:
    response = await client.get(f"{auth_service_url}/user/{user_id}")
```

Benefits:
- Simple and well-understood
- Easy to debug
- Works with circuit breaker

### Future: Asynchronous (Message Queue)

For event-driven architecture, consider:
- RabbitMQ or Kafka for event bus
- Publish domain events from aggregates
- Subscribe to events in other services

## Database Strategy

### Database per Service

Each service has its own PostgreSQL database:
- `auth_db` - Auth service
- `gateway_db` - Gateway service
- `aggregation_db` - Aggregation service

Benefits:
- Service independence
- Easier to scale
- Clear ownership
- Technology flexibility

Challenges:
- No foreign keys across services
- Eventual consistency
- Distributed transactions (use Saga pattern)

### Migrations

Each service manages its own migrations:

```bash
# Auth service
cd services/auth-service
poetry run alembic revision --autogenerate -m "Add users table"
poetry run alembic upgrade head
```

## Security

### Authentication Flow

1. User sends credentials to `/auth/login`
2. Auth service validates credentials
3. Auth service generates JWT access and refresh tokens
4. Gateway validates tokens on subsequent requests
5. Requests forwarded to backend services

### Token Structure

Access token (30 min):
```json
{
  "sub": "user-id",
  "type": "access",
  "roles": ["user", "admin"],
  "exp": 1234567890
}
```

Refresh token (7 days):
```json
{
  "sub": "user-id",
  "type": "refresh",
  "exp": 1234567890
}
```

### Password Security

- bcrypt hashing with salt
- Minimum 8 characters
- Stored as PasswordHash value object
- Never logged or returned in APIs

## Observability

### Structured Logging

All logs are JSON for easy parsing:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "event": "user_login",
  "user_id": "123",
  "duration_ms": 50
}
```

### Metrics

Prometheus metrics collected:
- Request rate and duration
- Database query performance
- Cache hit rates
- Business operations (registrations, logins)

### Tracing

OpenTelemetry for distributed tracing:
- Trace requests across services
- Identify bottlenecks
- Debug production issues

## Testing Strategy

### Test Pyramid

```
      /\
     /E2E\      ← Few, slow, expensive
    /------\
   /Integration\  ← Some, medium speed
  /-------------\
 /   Unit Tests  \ ← Many, fast, cheap
/________________\
```

### Test Coverage Requirements

- Domain: 100%
- Application: 95%
- Adapters: 85%
- Infrastructure: 70%

### Test Organization

```
tests/
├── unit/           # Fast, no I/O
│   ├── domain/
│   └── application/
├── integration/    # Real database
│   └── adapters/
└── e2e/           # Full API tests
    └── scenarios/
```

## Performance Considerations

### Caching Strategy

1. **Response Caching**: Cache GET responses in Redis
2. **Database Query Caching**: Cache expensive queries
3. **Session Storage**: Store user sessions in Redis

### Rate Limiting

- Redis sliding window algorithm
- Per-user or per-IP limits
- Configurable thresholds
- Graceful degradation

### Circuit Breaker

- Prevents cascading failures
- Opens after N failures
- Half-open state for testing recovery
- Configurable timeout and threshold

## Scalability

### Horizontal Scaling

All services are stateless and can be scaled horizontally:

```bash
docker-compose up --scale auth-service=3
docker-compose up --scale gateway-service=2
```

### Database Scaling

- Read replicas for queries
- Connection pooling
- Database per service allows independent scaling

### Caching

Redis for:
- Session storage
- Response caching
- Rate limiting counters
- Circuit breaker state

## Future Enhancements

1. **API Versioning**: Header-based versioning
2. **GraphQL Gateway**: Unified API for frontend
3. **Event Sourcing**: Audit trail and temporal queries
4. **CQRS**: Separate read and write models
5. **Saga Pattern**: Distributed transactions
6. **Service Mesh**: Istio or Linkerd for advanced routing

