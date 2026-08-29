from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import invalid_credentials, oauth2_scheme
from ..models.user import User

settings = get_settings()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        subject = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]).get("sub")
        user_id = int(subject)
    except (JWTError, TypeError, ValueError):
        raise invalid_credentials()
    user = db.scalar(select(User).where(User.id == user_id, User.is_active == True))  # noqa: E712
    if not user:
        raise invalid_credentials()
    return user
