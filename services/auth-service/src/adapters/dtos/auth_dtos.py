"""DTOs for authentication endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
    """Request DTO for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., min_length=1, description="User's full name")
    roles: list[str] | None = Field(default=None, description="Optional list of roles")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                    "full_name": "John Doe",
                    "roles": ["user"],
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response DTO for user data."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User's full name")
    status: str = Field(..., description="User account status")
    email_verified: bool = Field(..., description="Whether email is verified")
    roles: list[str] = Field(..., description="User roles")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "status": "active",
                    "email_verified": False,
                    "roles": ["user"],
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        }
    }


class AuthenticationRequest(BaseModel):
    """Request DTO for user authentication."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                }
            ]
        }
    }


class AuthenticationResponse(BaseModel):
    """Response DTO for successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserResponse = Field(..., description="User information")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "status": "active",
                        "email_verified": True,
                        "roles": ["user"],
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Request DTO for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "examples": [{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}]
        }
    }


class RefreshTokenResponse(BaseModel):
    """Response DTO for token refresh."""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Response DTO for errors."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    detail: str | None = Field(default=None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "invalid_credentials",
                    "message": "Invalid email or password",
                    "detail": None,
                }
            ]
        }
    }

