import pytest


@pytest.fixture(scope="module")
def openapi_schema_base():
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
def openapi_schema_simple(openapi_schema_base):
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
def openapi_schema(openapi_schema_base):
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
def openapi_schema_single_exc(openapi_schema):
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
def openapi_schema_multi_exc(openapi_schema):
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