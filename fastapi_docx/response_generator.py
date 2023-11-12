from typing import Any, TypeVar

from fastapi.openapi.constants import REF_TEMPLATE
from fastapi.routing import APIRoute
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema
from starlette.exceptions import HTTPException

from fastapi_docx.exception_finder import ErrType

ErrSchema = TypeVar("ErrSchema", bound=BaseModel)


class HTTPExceptionSchema(BaseModel):
    detail: str | None = None


def get_model_definition(model: type[BaseModel]) -> tuple[str, dict[str, Any]]:
    model_name = model.__name__
    schema_generator = GenerateJsonSchema(by_alias=True, ref_template=REF_TEMPLATE)
    m_schema = schema_generator.generate(
        model.__pydantic_core_schema__, mode="serialization"
    )
    if "description" in m_schema:
        m_schema["description"] = m_schema["description"].split("\f")[0]
    return model_name, m_schema


def add_model_to_openapi(api_schema: dict[str, Any], model: type[BaseModel]) -> None:
    model_name, m_schema = get_model_definition(model)
    if "components" not in api_schema:
        api_schema["components"] = {"schemas": {}}
    if "schemas" not in api_schema["components"]:
        api_schema["components"]["schemas"] = {}
    api_schema["components"]["schemas"][model_name] = m_schema


def write_response(
    api_schema: dict,
    route: APIRoute,
    exc: HTTPException,
    customError: type[ErrType] | None,
    customErrSchema: type[ErrSchema] | None,
) -> None:
    path = getattr(route, "path")
    methods = [method.lower() for method in getattr(route, "methods")]
    for method in methods:
        status_code = str(exc.status_code)
        if status_code not in api_schema["paths"][path][method]["responses"]:
            if customError and customErrSchema and isinstance(exc, customError):
                api_schema["paths"][path][method]["responses"][status_code] = {
                    "description": exc.__class__.__name__,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{customErrSchema.__name__}"
                            }
                        }
                    },
                }
            else:
                api_schema["paths"][path][method]["responses"][status_code] = {
                    "description": exc.detail,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/HTTPExceptionSchema"
                            }
                        }
                    },
                }
