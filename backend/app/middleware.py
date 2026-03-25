"""
Middleware for request handling, rate limiting, and error management.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Callable
import time
import logging
import os
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.
    Uses in-memory storage (for production, use Redis).
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests: dict = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
        
        # Record request
        self.client_requests[client_ip].append(current_time)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.client_requests[client_ip])
        )
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "client_ip": request.client.host,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params)
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "path": request.url.path
                }
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            logger.error(
                f"Error processing request: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e)
                }
            )
            raise

class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware for better control.
    """
    
    def __init__(self, app: ASGIApp, allow_origins: list = None):
        super().__init__(app)
        self.allow_origins = allow_origins or [
            "http://localhost:3000",
            "http://localhost:8000"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        origin = request.headers.get("origin")
        
        if origin in self.allow_origins or "*" in self.allow_origins:
            if request.method == "OPTIONS":
                return JSONResponse(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin or "*",
                        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type,Authorization",
                        "Access-Control-Max-Age": "86400",
                    }
                )
            
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            return response
        
        return await call_next(request)

def setup_logging(log_level: str = "INFO"):
    """
    Setup structured logging for the application.
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class ErrorHandler:
    """
    Global error handler for consistent error responses.
    """
    
    @staticmethod
    def handle_error(status_code: int, message: str, detail: str = None):
        """Return a standardized error response"""
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": message,
                "detail": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Exception classes
class TrendNexAIException(Exception):
    """Base exception for TrendNexAI"""
    
    def __init__(self, message: str, status_code: int = 400, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail

class AuthenticationException(TrendNexAIException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationException(TrendNexAIException):
    """Not authorized to access resource"""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class ValidationException(TrendNexAIException):
    """Validation failed"""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, status_code=422, detail=detail)

class ResourceNotFound(TrendNexAIException):
    """Resource not found"""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404)
