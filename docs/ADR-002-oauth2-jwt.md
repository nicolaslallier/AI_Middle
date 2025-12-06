# ADR-002: OAuth2 with JWT for Authentication

**Status**: Accepted  
**Date**: 2024-01-01  
**Decision Makers**: Development Team

## Context

We need a secure, scalable authentication mechanism for our microservices architecture. The solution must:
- Support multiple client types (web, mobile, third-party)
- Be stateless for horizontal scaling
- Provide short-lived access tokens
- Support token refresh without re-authentication

## Decision

We will implement **OAuth2 Authorization Code Flow with JWT tokens**:
- **Access tokens**: JWT, 30-minute expiration
- **Refresh tokens**: JWT, 7-day expiration
- **Token storage**: No server-side session storage
- **Algorithm**: HS256 (symmetric signing)

## Alternatives Considered

### 1. Session-Based Authentication
- **Pros**: Simple, well-understood, immediate revocation
- **Cons**: Not stateless, requires session store, harder to scale

### 2. OAuth2 with Opaque Tokens
- **Pros**: Tokens can be revoked, more secure
- **Cons**: Requires token validation call on every request, performance impact

### 3. API Keys
- **Pros**: Simple implementation
- **Cons**: No expiration, harder to manage, less secure

## Rationale

JWT with OAuth2 provides:

1. **Stateless Authentication**: No database lookup on every request
2. **Horizontal Scaling**: No shared session storage needed
3. **Mobile Support**: Works well with mobile apps
4. **Decentralized**: Services can verify tokens independently
5. **Standard Protocol**: OAuth2 is industry standard

## Implementation Details

### Token Structure

Access Token:
```json
{
  "sub": "user-id",
  "type": "access",
  "roles": ["user", "admin"],
  "exp": 1234567890,
  "iat": 1234567860
}
```

Refresh Token:
```json
{
  "sub": "user-id",
  "type": "refresh",
  "exp": 1234567890,
  "iat": 1234567860
}
```

### Security Measures

1. **Short-lived access tokens** (30 min) - limits exposure
2. **HTTPS only** - prevent token interception
3. **bcrypt password hashing** - protect stored passwords
4. **Token refresh** - user doesn't need to re-login
5. **User roles in token** - authorization without DB lookup

### Token Lifecycle

```
1. User logs in → Auth service validates
2. Auth service generates access + refresh tokens
3. Client stores tokens securely
4. Client includes access token in requests
5. Access token expires → Client uses refresh token
6. Auth service validates refresh token → Issues new access token
7. Refresh token expires → User must re-login
```

## Consequences

### Positive

- Horizontal scaling without session storage
- Fast authentication (no DB lookup per request)
- Works with any client type
- Industry-standard protocol

### Negative

- Cannot immediately revoke tokens (must wait for expiration)
- Token payload size (embedded in every request)
- Requires secure secret key management
- Refresh token rotation not implemented (future enhancement)

## Security Considerations

### Mitigations for Token Theft

1. **Short expiration**: Access tokens expire in 30 minutes
2. **HTTPS only**: Never send tokens over HTTP
3. **HttpOnly cookies**: If using cookies (future)
4. **Token blacklist**: Can be added if needed (trades statelessness)

### Secret Key Management

- Never commit secret key to repository
- Use environment variables or secret management service
- Rotate keys periodically in production
- Different keys per environment

## Future Enhancements

1. **Refresh Token Rotation**: Issue new refresh token on refresh
2. **Token Blacklist**: Track revoked tokens (Redis)
3. **Asymmetric Keys**: Use RS256 for multi-service scenarios
4. **Token Introspection**: Endpoint to validate tokens
5. **Scope-based Permissions**: Fine-grained authorization

## Compliance

- All authentication must use this JWT-based system
- No session-based auth in new code
- Tokens must be verified on protected endpoints
- Follow security best practices in implementation

## References

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

