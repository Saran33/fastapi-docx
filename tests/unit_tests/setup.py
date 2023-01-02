from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_docx import custom_openapi


class OpenApiTest:
    def setup_method(self, app: FastAPI) -> None:
        self.app = app
        self.app.openapi = custom_openapi(self.app)
        self.client = TestClient(self.app)

    def teardown_method(self) -> None:
        pass
