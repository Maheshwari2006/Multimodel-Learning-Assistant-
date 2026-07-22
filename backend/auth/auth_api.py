from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database import schemas
from backend.database.crud import (
    create_user,
    authenticate_user,
    get_user_by_email,
)
from backend.auth.jwt_handler import create_access_token
from backend.auth.oauth2 import get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.UserResponse
)
def register(
    request: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(
        db,
        request.email
    )

    if user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return create_user(
        db,
        request
    )


@router.post(
    "/login",
    response_model=schemas.Token
)
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        request.username,
        request.password
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user