from fastapi import APIRouter, FastAPI, HTTPException

from tests.unit_tests.fixtures.custom_exceptions import (
    AppExc,
    AppExceptionCase,
    AppExecptionSchema,
    RetryWith,
    app_exception_handler,
)
from tests.unit_tests.fixtures.services import AppService, UserService
from tests.unit_tests.setup import OpenApiTest

router = APIRouter()


def raise_error():
    if not 2 > 1:
        raise HTTPException(
            status_code=445,
            detail="TESTING ERROR 2",
        )
    else:
        return 1


@router.get("/", response_model=list)
def get_user(user_in):
    result = UserService.get_user(user_in)
    if not user_in:
        raise AppExc.CreateFailed({"obj": "User"})
    elif user_in == "Saran":
        raise RetryWith(context="abc")
    return result


@router.post("/")
def create_user(user_in):
    result = UserService().create_user(user_in)
    raise_error()
    user_serv = UserService()
    user_serv.do_something(user_in)
    if not user_in:
        raise AppExc.CreateFailed({"obj": "User"})
    if not 2 > 1:
        raise HTTPException(
            status_code=447,
            detail="TESTING ERROR 447",
        )
    return result


app = FastAPI(title="FastAPI", openapi_url="/api/v1/openapi.json")


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(router, prefix="/api/v1")


class TestServExc(OpenApiTest):
    def setup_method(self):
        super().setup_method(
            app,
            customError=AppExceptionCase,
            customErrSchema=AppExecptionSchema,
            serviceClasses=(AppService,),
        )

    def test_service_exceptions(self, services_openapi_schema: dict):
        expected_excs = {
            "get": ["500", "449", "444", "400"],
            "post": ["500", "447", "445", "409", "449", "444", "400"],
        }
        self.check_openapi_response_schema(
            services_openapi_schema, expected_excs, path=""
        )
