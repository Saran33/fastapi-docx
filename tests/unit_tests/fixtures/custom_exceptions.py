from typing import Any

from fastapi import Request
from fastapi.utils import is_body_allowed_for_status_code
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response


class AppExecptionSchema(BaseModel):
    exception: str | None = None
    detail: str | None = None
    context: dict[str, Any] | None = None


class AppExceptionCase(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        context: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ):
        self.case = self.__class__.__name__
        self.status_code = status_code
        self.headers = headers
        self.detail = detail
        self.context = context or ""


async def app_exception_handler(
    request: Request, exc: AppExceptionCase
) -> JSONResponse:
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "exception": exc.case,
            "detail": exc.detail,
            "context": exc.context,
        },
    )


class AppExc:
    class CreateFailed(AppExceptionCase):
        def __init__(self, context: dict[str, Any] | None = None):
            self.context = context or {}
            status_code = 500
            obj = self.context.get("obj", "object")
            detail = f"{obj} creation failed"
            super().__init__(status_code, detail)

    class ConnectionClosed(AppExceptionCase):
        def __init__(self) -> None:
            status_code = 444
            detail = "Conection closed without response"
            super().__init__(status_code, detail)

    class Unauthorized(AppExceptionCase):
        def __init__(self, context: dict[str, Any] | None = None):
            status_code = 401
            detail = "permission required"
            super().__init__(status_code, detail, context)


class RetryWith(AppExceptionCase):
    def __init__(self, context: dict[str, Any] | None = None):
        status_code = 449
        detail = "Retry the request"
        super().__init__(status_code, detail, context)


class TooManyRequests(AppExceptionCase):
    def __init__(self, context: dict[str, Any] | None = None):
        status_code = 420
        detail = "Too many requests"
        super().__init__(status_code, detail, context)
