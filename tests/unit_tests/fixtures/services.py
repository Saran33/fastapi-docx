from typing import Any

from fastapi import Depends, HTTPException, status

from tests.unit_tests.fixtures.custom_exceptions import AppExc, RetryWith
from tests.unit_tests.fixtures.dependencies import UserDeps


class AppService:
    pass


class UserService(AppService):
    @staticmethod
    def get_user(user_id: int) -> dict[str, Any]:
        user = {"name": "Saran", "id": user_id}
        if not user_id:
            raise AppExc.ConnectionClosed()
        elif user_id == 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"
            )
        return user

    def create_user(self, user: dict[str, Any]) -> dict[str, Any]:
        if not user:
            raise HTTPException(status_code=409, detail="TESTING ERROR")
        elif user == "Saran":
            raise RetryWith({"obj": "User"})
        elif not getattr(user, "name"):
            raise AppExc.ConnectionClosed()
        return {"name": "Saran", "id": 2}

    def do_something(self, user: dict[str, Any]) -> dict[str, Any]:
        if not user:
            raise HTTPException(status_code=400, detail="BAD REQUEST")
        return {"name": "Saran", "id": 2}

    @classmethod
    def get_authenticated(
        cls,
        user_id: int,
        current_user: dict[str, Any] = Depends(UserDeps.require_auth),
    ) -> dict[str, Any]:
        return {"name": "Saran", "id": 2}
