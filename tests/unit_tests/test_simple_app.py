from fastapi import FastAPI

from tests.unit_tests.setup import OpenApiTest

app = FastAPI()


@app.get("/")
def home():
    return "Hello World!"


class TestSimpleApp(OpenApiTest):
    def setup_method(self):
        super().setup_method(app)

    def test_simple_app(self, openapi_schema_simple: dict):
        res = self.client.get("/")
        assert res.status_code == 200

        res = self.client.get("/openapi.json/")
        assert res.json() == openapi_schema_simple
