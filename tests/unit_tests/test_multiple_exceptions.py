from fastapi import Depends, FastAPI, HTTPException

from tests.unit_tests.setup import OpenApiTest

app = FastAPI()


def raise_another():
    raise HTTPException(status_code=200, detail="Raise another")


async def get_another_user():
    raise HTTPException(status_code=500, detail="Get another user")


def get_user(opa: str = Depends(get_another_user)):
    raise HTTPException(status_code=201, detail="GET USER FAIL")


@app.get("/")
def home(item: int, user: str = Depends(get_user)):
    if item == 1:
        raise HTTPException(status_code=404, detail="Not found because...")
    raise_another()


class TestMultiExc(OpenApiTest):
    def setup_method(self):
        super().setup_method(app)

    def test_multiple_exceptions(self, openapi_schema_multi_exc: dict):
        openapi = self.client.get("/openapi.json/")
        assert openapi.json() == openapi_schema_multi_exc
