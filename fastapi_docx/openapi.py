from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from fastapi_docx.exception_finder import ErrType, RouteExcFinder
from fastapi_docx.response_generator import (
    ErrSchema,
    HTTPExceptionSchema,
    add_model_to_openapi,
    write_response,
)


def custom_openapi(
    app: FastAPI,
    customError: type[ErrType] | None = None,
    customErrSchema: type[ErrSchema] | None = None,
    HTTPExcSchema: type[ErrSchema] = HTTPExceptionSchema,
    dependencyClasses: tuple[type] | None = None,
    serviceClasses: tuple[type] | None = None,
) -> Callable:
    """Modify the OpenAPI specification for a FastAPI app to include any `HTTPException` raised in service classes and/or dependency classes.

    Optionally include custom exceptions and their schemas in the OpenAPI specification.

    Optionally include service classes and/or dependency classes.
    Specified service and dependency classes will be scanned for both HTTPExceptions and custom exceptions.

    Parameters:
        `app`: The FastAPI app for which to generate the OpenAPI specification.
        `customError`: A custom exception class that should be included in the OpenAPI specification.
                       All subclasses of the `customError` will be found and added to the spec.
                       Note: any custom error should be able to be instantiated without required arguments.
                       If paramaterizing your custom exceptions, ensure they use default kwargs.
        `customErrSchema`: The schema for the `customError` exception class.
        `HTTPExcSchema`: The schema for fastAPI/starlette HTTPExceptions raised by the app.
                         Defaults to one field: `detail: Optional[str]`
        `dependencyClasses`: A tuple of classes that represent dependencies for the app's routes.
                             You can subclass all dependencies and pass only the base e.g. `dependencyClasses=(BaseDependency,)`
        `serviceClasses`: A tuple of classes that represent service classes for the app's routes.
                          You can subclass all services and pass only the base e.g. `serviceClasses=(BaseService,)`
    Returns:
        A callable that returns the modified OpenAPI specification as a dictionary or else None.
    """

    def _custom_openapi() -> Any:
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        add_model_to_openapi(openapi_schema, HTTPExcSchema)
        if customErrSchema:
            add_model_to_openapi(openapi_schema, customErrSchema)
        finder = RouteExcFinder(customError, dependencyClasses, serviceClasses)
        for route in app.routes:
            if getattr(route, "include_in_schema", None):
                for exception in finder.extract_exceptions(route):
                    write_response(
                        openapi_schema,
                        route,
                        exception,
                        customError,
                        customErrSchema,
                    )
                finder.clear()
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return _custom_openapi
