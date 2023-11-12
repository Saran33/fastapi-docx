from fastapi import APIRouter, Depends, FastAPI

from tests.unit_tests.fixtures.custom_exceptions import (
    AppExceptionCase,
    AppExecptionSchema,
    app_exception_handler,
)
from tests.unit_tests.fixtures.dependencies import (
    AppDeps,
    CallableDep,
    CurrentUser,
    User,
    UserDeps,
)
from tests.unit_tests.fixtures.services import AppService, UserService
from tests.unit_tests.setup import OpenApiTest

router = APIRouter()


@router.get("/me")
def get_user(*, user_in, current_user: CurrentUser):
    result = UserService.get_authenticated(user_in)
    return result


@router.put("/me")
async def update_user(
    user_in, current_user: User = Depends(UserDeps.get_current_user_obj)
):
    result = UserService.get_authenticated(user_in)
    return result


callableInstance = CallableDep("bar")


@router.post("/me")
def create_user(
    *,
    user_in,
    has_name: bool = Depends(callableInstance),
):
    return user_in


user_dep = UserDeps(3)


@router.delete("/me")
def delete_user(
    *,
    user_id: int,
    some_dep: dict = Depends(user_dep.instance_method),
):
    return user_id


app = FastAPI(title="FastAPI", openapi_url="/api/v1/openapi.json")


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(router, prefix="/api/v1")


class TestDepExc(OpenApiTest):
    def setup_method(self):
        super().setup_method(
            app,
            customError=AppExceptionCase,
            customErrSchema=AppExecptionSchema,
            serviceClasses=(AppService,),
            dependencyClasses=(AppDeps, CallableDep),
        )

    def test_dependency_exceptions(self, dependencies_openapi_schema: dict):
        expected_excs = {
            "get": ["404", "420", "403", "401"],
            "put": ["404", "420", "403", "401"],
        }
        self.check_openapi_response_schema(
            dependencies_openapi_schema, expected_excs, path="me"
        )


# TestDepExc().setup_method()  # Uncomment and run this file to generate openapi docs in browser
