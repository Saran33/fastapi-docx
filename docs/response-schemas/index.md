### Generate schemas for the OpenAPI specification
- A default `HTTPExceptionSchema` will be added to the `OpenAPI` spec for every `HTTPException`. It defaults to one field: `detail: Optional[str]`.
```json
"HTTPExceptionSchema": {
                "title": "HTTPExceptionSchema",
                "type": "object",
                "properties": {"detail": {"title": "Detail", "type": "string"}},
            }

```
- The default schema can be modified by passing a `HTTPExcSchema` [Pydantic](https://github.com/pydantic/pydantic) model to the `custom_openapi` function:

```Python
from typing import Any
from pydantic import BaseModel
from fastapi_docx.openapi import custom_openapi


class CustomExcSchema(BaseModel):
    exception: str | None = None
    detail: str | None = None
    context: dict[str, Any] | None = None


app.openapi = custom_openapi(app, HTTPExcSchema=CustomExcSchema)

```
- Similarly, a `customErrSchema` can be passed to define the response structure for any `customError` class defined in your application.
