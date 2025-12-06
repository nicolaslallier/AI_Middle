# Deployment Issues Fixed

This document summarizes the issues encountered during the initial Docker deployment and how they were resolved.

## Issues Encountered

### 1. Poetry Lock Files Missing Metadata

**Problem**: The placeholder `poetry.lock` files created initially did not contain proper metadata, causing Poetry to fail during `poetry install` in the Docker build process.

**Error**:
```
The lock file does not have a metadata entry.
Regenerate the lock file with the `poetry lock` command.
```

**Solution**: Deleted the placeholder lock files and regenerated them using `poetry lock` command:
```bash
cd services/auth-service && poetry lock
cd services/gateway-service && poetry lock
cd services/aggregation-service && poetry lock
```

### 2. Port Conflicts

**Problem**: Ports 5432 (PostgreSQL) and 6379 (Redis) were already in use on the host machine.

**Error**:
```
Bind for 0.0.0.0:5432 failed: port is already allocated
Bind for 0.0.0.0:6379 failed: port is already allocated
```

**Solution**: Updated `docker-compose.yml` to use alternative ports:
- Auth DB: `5442:5432` (host:container)
- Redis: `6389:6379` (host:container)

### 3. Shared Common Library Not Accessible

**Problem**: Services could not import the `common` shared library because it wasn't included in the Docker build context.

**Error**:
```
ModuleNotFoundError: No module named 'common'
```

**Solution**:
1. Changed Docker build context in `docker-compose.yml` from service directory to project root
2. Updated all Dockerfiles to copy the `shared` directory and set `PYTHONPATH`:
   ```dockerfile
   COPY shared /app/shared
   ENV PYTHONPATH="/app/shared:${PYTHONPATH}"
   ```

### 4. Missing Module Exports

**Problem**: Several types and classes weren't exported from their respective `__init__.py` files.

**Errors**:
```
ImportError: cannot import name 'ErrorResponse' from 'src.adapters.dtos'
ImportError: cannot import name 'TokenType' from 'src.domain.value_objects'
```

**Solution**: Added missing exports to `__init__.py` files:
- `services/auth-service/src/adapters/dtos/__init__.py`: Added `ErrorResponse`
- `services/auth-service/src/domain/value_objects/__init__.py`: Added `TokenType`

### 5. Dataclass Field Ordering

**Problem**: Python dataclasses require all fields without defaults to come before fields with defaults. The `User` entity inherited from `BaseEntity` which had required fields (`created_at`, `updated_at`), but `User` also had required fields before optional ones.

**Error**:
```
TypeError: non-default argument 'email' follows default argument
```

**Solution**: Reordered fields in the `User` dataclass to respect Python's field ordering rules:
```python
@dataclass
class User(BaseEntity):
    # Required fields from BaseEntity first
    id: UserId
    created_at: datetime
    updated_at: datetime
    # Required fields from User
    email: Email
    password_hash: PasswordHash
    full_name: str
    status: UserStatus
    # Optional fields last
    email_verified: bool = False
    last_login_at: datetime | None = None
    roles: list[str] = field(default_factory=list)
```

## Final Configuration

### Services Running

All services are now running successfully:

- **Auth Service**: `http://localhost:8001`
- **Gateway Service**: `http://localhost:8002`
- **Aggregation Service**: `http://localhost:8003`

### Health Check Results

```bash
$ curl http://localhost:8001/health
{"status":"healthy","service":"auth-service"}

$ curl http://localhost:8002/health
{"status":"healthy","service":"gateway-service"}

$ curl http://localhost:8003/health
{"status":"healthy","service":"aggregation-service"}
```

### Database Ports

- Auth DB (PostgreSQL): `localhost:5442`
- Gateway DB (PostgreSQL): `localhost:5433`
- Aggregation DB (PostgreSQL): `localhost:5434`
- Redis: `localhost:6389`

## Commands Used

### Build and start all services:
```bash
docker-compose build
docker-compose up -d
```

### Check service status:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f auth-service
docker-compose logs -f gateway-service
docker-compose logs -f aggregation-service
```

### Stop all services:
```bash
docker-compose down
```

### Rebuild a specific service:
```bash
docker-compose build auth-service
docker-compose up -d auth-service
```

## Next Steps

1. Run database migrations for the Auth service:
   ```bash
   docker-compose exec auth-service alembic upgrade head
   ```

2. Test the API endpoints (currently only health checks are working)

3. Implement the remaining functionality in Gateway and Aggregation services

4. Add integration tests

5. Configure environment variables properly (currently using docker-compose defaults)

