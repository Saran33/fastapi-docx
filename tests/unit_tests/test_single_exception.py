from fastapi import FastAPI, HTTPException

from tests.unit_tests.setup import OpenApiTest

app = FastAPI()


@app.get("/{item_id}")
def get_item(item_id: int) -> str:
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found.")
    return "Item exists!"


class TestSingleExc(OpenApiTest):
    def setup_method(self):
        super().setup_method(app)

    def test_single_exception(self, openapi_schema_single_exc: dict):
        res = self.client.get("/1")
        assert res.status_code == 200

        res = self.client.get("/0")
        assert res.status_code == 404

        res = self.client.get("/openapi.json/")
        assert res.json() == openapi_schema_single_exc
