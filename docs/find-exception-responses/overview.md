## Quick Start
- In the below basic app, all of the possible `HTTPException` responses will be added to the openAPI spec.
```Python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi_docx import custom_openapi

app = FastAPI()


def raise_exc():
    raise HTTPException(status_code=400, detail="Some exception")


def get_user(opa: str = Depends(get_another_user)):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")


@app.get("/")
def home(item: int, user: str = Depends(get_user)):
    if item == 1:
        raise HTTPException(status_code=404, detail="Not found")
    raise_exc()


app.openapi = custom_openapi(app)

```

- Visiting <a href="http://localhost:8080/docs" class="external-link" target="_blank">http://localhost:8080/docs</a> (or whatever host and port your app is running on), should display the below documented responses:

![basic app example docs](https://saran33.github.io/fastapi-docx/img/fastapi-docx_basic_example.png)
