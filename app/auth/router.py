from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, ResetPassword, ForgotPassword, UserUpdate
from app.auth.services import AuthService
from app.database import get_db
from fastapi import Form, File, UploadFile
from typing import Optional
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.auth.dependencies import get_current_user, oauth2_scheme
from app.models.accessToken import AccessToken
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/social-login")
async def social_login(
    id_token: str = Form(...),
    auth_provider: str = Form(...),
    db: Session = Depends(get_db)
):
    from firebase_admin import auth

    try:
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token["email"]
        name = decoded_token.get("name", "Unknown")
        picture = decoded_token.get("picture")

        user = AuthService.create_user_from_social_login(db, name, email, picture, auth_provider)
        response = AuthService.generate_login_token(db, user, auth_provider=auth_provider)

        profile_image = user.profile_image
        if profile_image:
            if profile_image.startswith("http://") or profile_image.startswith("https://"):
                image_url = profile_image
            else:
                image_url = f"https://mellowmind-production-457f.up.railway.app/uploads/{profile_image}"
        else:
            image_url = None

        if "data" in response:
            response["data"]["profile_image"] = image_url
        elif "user" in response:
            response["user"]["profile_image"] = image_url

        return response

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")


@router.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user_data = type("UserData", (object,), {
        "name": name,
        "email": email,
        "password": password,
        "profile_image": profile_image
    })()

    return AuthService.register_user(db, user_data)

@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return AuthService.authenticate_user(db, email, password)

@router.post("/reset-password")
async def reset_password(
    email: str = Form(...),
    new_password: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    return AuthService.reset_password(db, email, new_password, token)

@router.post("/forgot-password")
async def forgot_password(
    email: str = Form(...), 
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    return AuthService.initiate_password_reset(db, email)

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    token_entry = db.query(AccessToken).filter_by(user_id=current_user.id, token=token).first()
    
    if not token_entry:
        return JSONResponse(
            status_code=200,
            content={"status": 200, "message": "Invalid token or already logged out"}
        )

    db.delete(token_entry)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={"status": 200, "message": "Logout successful"}
    )

@router.post("/users/{user_id}")
async def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to update this user.")

    return AuthService.update_user(db, user_id, name, email, profile_image)
