from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CodigoTOTP = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
UUIDTexto = Field(pattern=r"^[0-9a-fA-F-]{36}$")
TokenTexto = Field(min_length=10, max_length=4096)


class InscribirMFAResponse(BaseModel):
    factor_id: str
    qr_code: str
    secret: str


class ConfirmarMFARequest(BaseModel):
    factor_id: str = UUIDTexto
    codigo: str = CodigoTOTP


class DesactivarMFARequest(BaseModel):
    factor_id: str = UUIDTexto
    password: str = Field(min_length=1, max_length=128)
    codigo: str = CodigoTOTP


class LoginRequest(BaseModel):
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+$")
    password: str = Field(min_length=1, max_length=128)


class LoginMFARequest(BaseModel):
    factor_id: str = UUIDTexto
    codigo: str = CodigoTOTP


class RenovarRequest(BaseModel):
    access_token: str = TokenTexto
    refresh_token: str = Field(min_length=5, max_length=512)


class LoginResponse(BaseModel):
    estado: Literal["ok", "mfa_required"]
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    mfa_token: str | None = None
    factor_id: str | None = None


class SesionOut(BaseModel):
    sesion_id: str
    dispositivo_info: str | None
    ip_origen: str | None
    creado_en: datetime
    ultimo_uso_en: datetime
    actual: bool
