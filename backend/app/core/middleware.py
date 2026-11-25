from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Rutas bajo /api que no requieren token
PUBLIC_PATHS = {"/api/auth/login", "/api/auth/register"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Autenticación: rechaza con 401 toda petición a /api/* sin un JWT válido.

    La autorización (¿es el dueño del recurso?) depende del recurso concreto y
    se aplica en las dependencias de cada router (require_board_owner, etc.).
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if (
            request.method == "OPTIONS"  # preflight CORS
            or not path.startswith("/api/")
            or path in PUBLIC_PATHS
        ):
            return await call_next(request)

        unauthorized = JSONResponse(
            status_code=401,
            content={"detail": "Could not validate credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            return unauthorized
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            return unauthorized
        if payload.get("sub") is None:
            return unauthorized

        request.state.user_id = int(payload["sub"])
        return await call_next(request)
