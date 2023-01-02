from typing import Any

import pytest


@pytest.fixture(scope="module")
def openapi_schema_base() -> dict[str, Any]:
    return {
        "openapi": "3.0.2",
        "info": {"title": "FastAPI", "version": "0.1.0"},
        "components": {
            "schemas": {
                "HTTPExceptionSchema": {
                    "title": "HTTPExceptionSchema",
                    "type": "object",
                    "properties": {"detail": {"title": "Detail", "type": "string"}},
                }
            }
        },
    }


@pytest.fixture(scope="module")
def openapi_schema_simple(openapi_schema_base: dict[str, Any]) -> dict[str, Any]:
    _openapi_schema = openapi_schema_base.copy()
    _openapi_schema["paths"] = {
        "/": {
            "get": {
                "summary": "Home",
                "operationId": "home__get",
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    }
                },
            }
        }
    }
    return _openapi_schema


@pytest.fixture(scope="module")
def openapi_schema(openapi_schema_base: dict[str, Any]) -> dict[str, Any]:
    _openapi_schema = openapi_schema_base.copy()
    _openapi_schema["components"]["schemas"].update(
        {
            "HTTPValidationError": {
                "title": "HTTPValidationError",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ValidationError"},
                    }
                },
            },
            "ValidationError": {
                "title": "ValidationError",
                "required": ["loc", "msg", "type"],
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Location",
                        "type": "array",
                        "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                    },
                    "msg": {"title": "Message", "type": "string"},
                    "type": {"title": "Error Type", "type": "string"},
                },
            },
        }
    )

    return _openapi_schema


@pytest.fixture(scope="module")
def openapi_schema_single_exc(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    _openapi_schema = openapi_schema.copy()
    _openapi_schema["paths"] = {
        "/{item_id}": {
            "get": {
                "summary": "Get Item",
                "operationId": "get_item__item_id__get",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "Item Id", "type": "integer"},
                        "name": "item_id",
                        "in": "path",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Item not found.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                },
            }
        }
    }
    return _openapi_schema


@pytest.fixture(scope="module")
def openapi_schema_multi_exc(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    _openapi_schema = openapi_schema.copy()
    _openapi_schema["paths"] = {
        "/": {
            "get": {
                "summary": "Home",
                "operationId": "home__get",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "Item", "type": "integer"},
                        "name": "item",
                        "in": "query",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Not found because...",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "201": {
                        "description": "GET USER FAIL",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "500": {
                        "description": "Get another user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                },
            }
        }
    }
    return _openapi_schema


@pytest.fixture(scope="module")
def openapi_schema_components() -> dict[str, Any]:
    return {
        "schemas": {
            "HTTPValidationError": {
                "title": "HTTPValidationError",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ValidationError"},
                    }
                },
            },
            "ValidationError": {
                "title": "ValidationError",
                "required": ["loc", "msg", "type"],
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Location",
                        "type": "array",
                        "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                    },
                    "msg": {"title": "Message", "type": "string"},
                    "type": {"title": "Error Type", "type": "string"},
                },
            },
            "HTTPExceptionSchema": {
                "title": "HTTPExceptionSchema",
                "type": "object",
                "properties": {"detail": {"title": "Detail", "type": "string"}},
            },
            "AppExecptionSchema": {
                "title": "AppExecptionSchema",
                "type": "object",
                "properties": {
                    "exception": {"title": "Exception", "type": "string"},
                    "detail": {"title": "Detail", "type": "string"},
                    "context": {"title": "Context", "type": "object"},
                },
            },
        }
    }


@pytest.fixture(scope="module")
def services_openapi_schema(
    openapi_schema_base: dict[str, Any],
    openapi_schema_components: dict[str, Any],
) -> dict[str, Any]:
    _openapi_schema = openapi_schema_base.copy()
    _openapi_schema["paths"] = {
        "/api/v1/": {
            "get": {
                "summary": "Get User",
                "operationId": "get_user_api_v1__get",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User In"},
                        "name": "user_in",
                        "in": "query",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "title": "Response Get User Api V1  Get",
                                    "type": "array",
                                    "items": {},
                                }
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "500": {
                        "description": "CreateFailed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "449": {
                        "description": "RetryWith",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "444": {
                        "description": "ConnectionClosed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                },
            },
            "post": {
                "summary": "Create User",
                "operationId": "create_user_api_v1__post",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User In"},
                        "name": "user_in",
                        "in": "query",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "500": {
                        "description": "CreateFailed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "447": {
                        "description": "TESTING ERROR 447",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "445": {
                        "description": "TESTING ERROR 2",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "409": {
                        "description": "TESTING ERROR",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "449": {
                        "description": "RetryWith",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "444": {
                        "description": "ConnectionClosed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "BAD REQUEST",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                },
            },
        }
    }
    _openapi_schema["components"] = openapi_schema_components.copy()
    return _openapi_schema


@pytest.fixture(scope="module")
def dependencies_openapi_schema(
    openapi_schema_base: dict[str, Any], openapi_schema_components: dict[str, Any]
) -> dict[str, Any]:
    _openapi_schema = openapi_schema_base.copy()
    _openapi_schema["paths"] = {
        "/api/v1/me": {
            "get": {
                "summary": "Get User",
                "operationId": "get_user_api_v1_me_get",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User In"},
                        "name": "user_in",
                        "in": "query",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "420": {
                        "description": "TooManyRequests",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Could not validate credentials",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                },
            },
            "put": {
                "summary": "Update User",
                "operationId": "update_user_api_v1_me_put",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User In"},
                        "name": "user_in",
                        "in": "query",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "420": {
                        "description": "TooManyRequests",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Could not validate credentials",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                },
            },
            "post": {
                "summary": "Create User",
                "operationId": "create_user_api_v1_me_post",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User In"},
                        "name": "user_in",
                        "in": "query",
                    },
                    {
                        "required": False,
                        "schema": {"title": "Kwarg", "type": "string", "default": ""},
                        "name": "kwarg",
                        "in": "query",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                },
            },
            "delete": {
                "summary": "Delete User",
                "operationId": "delete_user_api_v1_me_delete",
                "parameters": [
                    {
                        "required": True,
                        "schema": {"title": "User Id", "type": "integer"},
                        "name": "user_id",
                        "in": "query",
                    },
                    {
                        "required": True,
                        "schema": {"title": "Id", "type": "integer"},
                        "name": "id",
                        "in": "query",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                    "407": {
                        "description": "Some other error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPExceptionSchema"
                                }
                            }
                        },
                    },
                    "444": {
                        "description": "ConnectionClosed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppExecptionSchema"
                                }
                            }
                        },
                    },
                },
            },
        }
    }
    _openapi_schema["components"] = openapi_schema_components.copy()
    return _openapi_schema
