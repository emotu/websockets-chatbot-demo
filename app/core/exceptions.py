from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class ServiceError(Exception):
    """Base exception for service layer errors"""

    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.error_type = "service_error"


class NotFoundError(ServiceError):
    """Raised when a resource is not found"""

    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "not_found"


class ConstraintViolationError(ServiceError):
    """Raised when database constraints are violated"""

    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.error_type = "constraint_violation"


class DatabaseError(ServiceError):
    """Raised when database operations fail"""

    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.error_type = "database_error"


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """Handle service layer errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc),
            "error_type": exc.error_type,
        },
    )


async def validation_error_handler(
    request: Request, exc: ValidationError | RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_type": "validation_error",
            "errors": exc.errors(),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "http_error"},
    )
