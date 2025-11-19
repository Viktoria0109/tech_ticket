from typing import Iterable, Union, Set
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.security import get_current_user

def require_role(required_roles: Union[int, Iterable[int]]):
    if isinstance(required_roles, int):
        required: Set[int] = {required_roles}
    else:
        required = set(required_roles)

    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа")
        return user

    return role_checker


