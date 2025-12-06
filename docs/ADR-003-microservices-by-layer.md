# ADR-003: Microservices Division by Technical Layer

**Status**: Accepted  
**Date**: 2024-01-01  
**Decision Makers**: Development Team

## Context

We need to decide how to divide the middleware application into microservices. Two main approaches:

1. **By Business Domain**: User service, Order service, Payment service
2. **By Technical Layer**: Auth service, Gateway service, Aggregation service

Given that the middleware primarily bridges frontend and backend (backend not yet built), we need a structure that:
- Provides clear technical boundaries
- Allows independent scaling
- Simplifies frontend integration
- Defines contracts for future backend

## Decision

We will divide microservices **by technical layer**:

1. **Auth Service**: OAuth2 authentication and authorization
2. **Gateway Service**: API gateway, routing, rate limiting, circuit breaker
3. **Aggregation Service**: Data aggregation, transformation, business logic orchestration

## Alternatives Considered

### 1. Business Domain Services
Example: User Service, Product Service, Order Service

- **Pros**: Clear business boundaries, team ownership
- **Cons**: Backend not yet built, unclear domain boundaries, premature splitting

### 2. Monolithic Middleware
Single service handling all middleware concerns

- **Pros**: Simpler to start, less operational overhead
- **Cons**: Harder to scale specific concerns, tight coupling

### 3. Backend for Frontend (BFF)
Separate middleware per client type

- **Pros**: Client-specific optimization
- **Cons**: Code duplication, multiple frontends not yet defined

## Rationale

Technical layer division provides:

1. **Clear Responsibilities**
   - Auth: Security and identity
   - Gateway: Traffic management
   - Aggregation: Business logic and data combination

2. **Independent Scaling**
   - Scale auth separately (CPU-intensive bcrypt)
   - Scale gateway separately (high traffic)
   - Scale aggregation separately (I/O-intensive)

3. **Technology Flexibility**
   - Each service can use optimal tech
   - Gateway could use Golang in future
   - Aggregation could add Celery workers

4. **Contract Definition**
   - Middleware defines contracts for future backend
   - Frontend knows what to expect
   - Backend can be built to match contracts

## Service Responsibilities

### Auth Service
- User registration and login
- Password management
- Token generation and validation
- User profile management
- Role-based access control

### Gateway Service
- Request routing to appropriate services
- Rate limiting per user/IP
- Circuit breaker for backend services
- Request/response logging
- API versioning

### Aggregation Service
- Combine data from multiple sources
- Apply business transformation rules
- Cache frequently accessed data
- Execute business logic workflows
- Provide unified API to frontend

## Communication Pattern

```
Frontend
   ↓
Gateway Service (entry point)
   ↓
   ├→ Auth Service (for auth endpoints)
   ├→ Aggregation Service (for business logic)
   └→ Future Backend Services
```

## Consequences

### Positive

- Clear separation of concerns
- Easy to understand responsibility boundaries
- Can scale each concern independently
- Simple deployment and monitoring
- Clear contracts for future backend

### Negative

- May need to split aggregation service by domain later
- Some code might not fit cleanly into these categories
- Overhead of running three services vs. one

## Migration Path

As the system grows:

1. **Phase 1** (Current): Three technical layer services
2. **Phase 2**: Split aggregation by domain (User Aggregation, Order Aggregation)
3. **Phase 3**: Backend services replace aggregation service calls
4. **Phase 4**: Aggregation becomes orchestration layer only

## Compliance

- New features must fit into one of the three services
- Cross-service communication must be documented
- No direct database access across services
- All inter-service communication via REST APIs

## Future Considerations

### When to Split Aggregation Service

Split aggregation service when:
- Clear domain boundaries emerge
- Different teams own different domains
- Need independent deployment cycles
- Performance requires domain-specific optimization

### When Backend is Built

Aggregation service evolution:
- Initially: Aggregation fetches from multiple backends
- Later: Aggregation becomes orchestration layer
- Finally: May consolidate with gateway if simple routing only

## References

- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/)
- [BFF Pattern](https://samnewman.io/patterns/architectural/bff/)
- Project docker-compose.yml

