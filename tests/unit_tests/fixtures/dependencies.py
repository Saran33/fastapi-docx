from collections.abc import Generator
from typing import Any

from fastapi import Depends, HTTPException, status

from tests.unit_tests.fixtures.custom_exceptions import AppExc, TooManyRequests


class AppDeps:
    pass


class Session:
    def __init__(self):
        self.bind = None


class User:
    def __init__(self, id: int = 1):
        self.id = id


class DbDeps(AppDeps):
    @staticmethod
    def get_db() -> Generator:
        try:
            db = Session()
            yield db
        except NameError:
            raise HTTPException(status_code=500, detail="Could not connect to db")
        except Exception:
            raise AppExc.ConnectionClosed()
        finally:
            pass


class UserDeps(AppDeps):
    user = {"name": "Person", "id": 2}

    def __init__(self, user_id: int | None = None):
        self.user_id = user_id

    @staticmethod
    def get_current_user() -> dict[str, Any]:
        try:
            user = UserDeps.user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["name"] == "bot":
            raise TooManyRequests(context=user)
        return user

    @staticmethod
    async def get_current_user_obj() -> User:
        try:
            user = User()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["name"] == "bot":
            raise TooManyRequests(context=user)
        return user

    @staticmethod
    def require_auth() -> dict[str, Any]:
        try:
            user = UserDeps.user
        except Exception:
            raise AppExc.Unauthorized(context=user)
        return user

    def instance_method(
        self, id: int, db: Session = Depends(DbDeps.get_db)
    ) -> dict[str, Any]:
        try:
            user = UserDeps.user
        except Exception:
            raise AppExc.ConnectionClosed()
        if id == 1:
            raise HTTPException(status_code=407, detail="Some other error")
        return user


class CallableDep:
    def __init__(self, arg: str):
        self.arg = arg

    def __call__(self, kwarg: str = ""):
        if not kwarg:
            raise HTTPException(status_code=400, detail="Bad request")
        return self.arg == kwarg
