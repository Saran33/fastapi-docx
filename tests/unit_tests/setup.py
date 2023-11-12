from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_docx import custom_openapi


class OpenApiTest:
    def setup_method(self, app: FastAPI, **kwargs) -> None:
        self.app = app
        self.app.openapi = custom_openapi(self.app, **kwargs)
        self.client = TestClient(self.app)

    def teardown_method(self) -> None:
        pass

    def check_openapi_response_schema(
        self,
        expected_schema: dict,
        expected_responses: dict[str, list[str]],
        path: str,
        router_prefix: str = "/api/v1",
    ):
        openapi = self.client.get(f"{router_prefix}/openapi.json")
        if (response_schema := openapi.json()) == expected_schema:
            assert True
        else:
            unfound_excs = []
            for method, expected_status_codes in expected_responses.items():
                _unfound_excs = self.find_missing_responses(
                    response_schema,
                    expected_schema,
                    expected_status_codes,
                    path=path,
                    method=method,
                    router_prefix=router_prefix,
                )
                unfound_excs += _unfound_excs

            import json

            with open(f"{self.__class__.__name__}_test_fail_response.json", "w") as f:
                json.dump(response_schema, f)
            with open(f"{self.__class__.__name__}_expected.json", "w") as f:
                json.dump(expected_schema, f)

            assert False

    def find_missing_responses(
        self,
        response_schema: dict,
        expected_schema: dict,
        expected_status_codes: list,
        path: str,
        method: str,
        router_prefix: str = "/api/v1",
    ):
        unfound_excs = []
        for exc in expected_status_codes:
            try:
                assert (
                    resp_exc := response_schema["paths"][f"{router_prefix}/{path}"][
                        method
                    ]["responses"].get(exc)
                ) == expected_schema["paths"][f"{router_prefix}/{path}"][method][
                    "responses"
                ][
                    exc
                ]
            except AssertionError:
                print(
                    f"{method.upper()} {exc} NOT FOUND IN RESPONSE SCHEMA"
                    if not resp_exc
                    else f"{method.upper()} {exc} DOES NOT MATCH EXPECTED SCHEMA"
                )
                unfound_excs.append(exc)

        return unfound_excs
