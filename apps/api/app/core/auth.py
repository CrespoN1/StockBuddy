"""
Clerk JWT verification.

Verifies JWTs issued by Clerk using their JWKS (JSON Web Key Set) endpoint.
The JWKS contains Clerk's public RSA keys used to sign tokens.
"""

import structlog

import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings

logger = structlog.stdlib.get_logger(__name__)

# Cache the JWKS client to avoid re-fetching keys on every request.
# Clerk rotates keys infrequently; PyJWKClient caches internally too.
_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        if not settings.clerk_jwks_url:
            raise RuntimeError(
                "CLERK_JWKS_URL is not set. "
                "Set it to https://<your-clerk-domain>/.well-known/jwks.json"
            )
        _jwks_client = PyJWKClient(settings.clerk_jwks_url, cache_keys=True)
    return _jwks_client


def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk-issued JWT and return the decoded payload.

    Returns the full decoded payload dict which includes:
      - sub: Clerk user ID (e.g., "user_2abc123...")
      - iss: Issuer URL
      - exp: Expiration timestamp
      - iat: Issued-at timestamp
      - azp: Authorized party (your frontend URL)

    Raises jwt.exceptions.PyJWTError on invalid/expired tokens.
    """
    client = _get_jwks_client()
    signing_key = client.get_signing_key_from_jwt(token)

    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        options={
            "verify_exp": True,
            "verify_aud": False,  # Clerk doesn't always set aud
        },
    )
    return decoded


def get_user_id_from_token(token: str) -> str:
    """Extract the Clerk user ID (sub claim) from a verified JWT.

    Raises jwt.exceptions.PyJWTError if the token is invalid.
    """
    payload = verify_clerk_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise jwt.exceptions.InvalidTokenError("Token missing 'sub' claim")
    return user_id
