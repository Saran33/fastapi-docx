### Find exceptions raised in class methods or callable class instances
- If your application is using classes for dependency-injection, or other classes for handling CRUD operations or business logic, you can specify these classes for inclusion in the OpenAPI spec.
- If any method owned by an instance of these dependency/service classes is called within a route (either directly or indirectly), every `HTTPException` raised within that method will be detected and added to the `OpenAPI` spec.
- Every `HTTPException` that might be raised within an instance method, `classmethod`, or `staticmethod` of a dependency class or a service class will be detected.
- The `dependencyClasses` and `serviceClasses` arguments passed to the `custom_openapi` function can either be a tuple of classes or a singleton base class from which all other service/dependency classes are derived.
- Any `HTTPException` raised within a [callable Dependency instance](https://fastapi.tiangolo.com/advanced/advanced-dependencies/#a-callable-instance) will also be detected.

### Dependency Classes
- A "dependency class" is defined here as any class that has a method called by the [FastAPI dependency injection system](https://fastapi.tiangolo.com/tutorial/dependencies/) (passed to the FastAPI `Depends` class, either in a path operation function or in any callable nested within a path operation).
- A common pattern would be to use a Base dependency class from which all other dependency classes inherit. The base class can then be passed to the `custom_openapi` function. The below example illustrates how to include every `HTTPException` raised within any class inheriting from a base `AppDeps` dependency class:

```Python
from fastapi import Depends, FastAPI, HTTPException, status


class AppDeps:
    pass


user = {"name": "Person", "id": 2}


class UserDeps(AppDeps):
    def __init__(self, user_id: int | None = None):
        self.user_id = user_id

    @staticmethod
    def require_auth():
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
            )
        return user

    def instance_method(self, id):
        if not id == user["id"]:
            raise HTTPException(status_code=407, detail="Some error")
        return user


app = FastAPI()


@app.get("/me")
def get_user(*, user_in, current_user=Depends(UserDeps.get_current_user)):
    return current_user


user_dep = UserDeps(3)


@app.delete("/me")
def delete_user(
    *,
    user_id: int,
    some_dep: dict = Depends(user_dep.instance_method),
):
    return user_id


app.openapi = custom_openapi(app, dependencyClasses=(AppDeps,))

```
- In the above (contrived) example, any `HTTPException` rasied by a `UserDeps` method will be added to the API docs. The `dependencyClasses` parameter of the `custom_openapi` function accepts a tuple of classes as an argument. These classes will be searched for exception responses. In this case, we are passing only the base class from which `UserDeps` inherits, but any number of classes can be specified.

### Service Classes
- A common pattern in FastAPI apps is to decouple business logic from endpoint functions by using some orchestration layer or "service". The term "service" is somewhat ambiguous. It could also incorporate some CRUD (Create Read Update Delete) / DAL (Data Access Layer) operations involving an ORM such as [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy). For our intents and purposes, in the context of `fastapi-docx`, it doesn't matter how you structure your app. A `service` here can refer to any class that has a method called within a route, which might raise an exception response that you want to document.
- Similarly to dependency classes, "service" classes can be passed to the `custom_openapi` function via the `serviceClasses` paramater:
```Python
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, status


class AppService:
    pass


class UserService(AppService):
    @staticmethod
    def get_user(user_id: int) -> dict[str, Any]:
        user = {"name": "Saran", "id": user_id}
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"
            )
        return user

    def create_user(self, user: dict[str, Any]) -> dict[str, Any]:
        if not user:
            raise HTTPException(status_code=444, detail="Conection closed")
        return {"name": "Saran", "id": 2}

    def do_something(self, user: dict[str, Any]) -> dict[str, Any]:
        if not user:
            raise HTTPException(status_code=400, detail="Bad request")
        return {"name": "Saran", "id": 2}

    @classmethod
    def get_authenticated(cls, user_id: int) -> dict[str, Any]:
        return {"name": "Saran", "id": user_id}


app = FastAPI()


@app.get("/")
def get_user(user_in):
    return UserService.get_user(user_in)


@app.post("/")
def create_user(user_in):
    user = UserService().create_user(user_in)
    user_serv = UserService()
    result = user_serv.do_something(user)
    if not result:
        raise HTTPException(
            status_code=420,
            detail="Too many requests"
        )
    return result


app.openapi = custom_openapi(app, serviceClasses=(AppService,))

```
