from pydantic import BaseModel, EmailStr


class AdminIn(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: EmailStr


class SuperAdminIn(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: EmailStr
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    password: str
    new_password: str
    confirm_new_password: str
