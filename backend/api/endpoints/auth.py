import os
import secrets
from datetime import datetime, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pymongo.errors import DuplicateKeyError

from api.classes import UsuarioLogin, UsuarioOut, UsuarioRegister
from db.mongo import mongo as mongo_db
from db.redis.redis_client import client as redis_client

load_dotenv()

SESSION_TTL = int(os.getenv("SESSION_TTL", "1800"))  # segundos (30 min por defecto)
COOKIE_NAME = "session_token"

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Helpers de contraseña ---

def hash_password(plano: str) -> str:
    return bcrypt.hashpw(plano.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(plano: str, hasheado: str) -> bool:
    try:
        return bcrypt.checkpw(plano.encode("utf-8"), hasheado.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --- Helpers de sesión (Redis) ---

def _session_key(token: str) -> str:
    return f"session:{token}"


def crear_sesion(usuario: dict) -> str:
    """Genera un token opaco y guarda la sesión como HASH con TTL en Redis."""
    token = secrets.token_urlsafe(32)
    redis_client.hset(
        _session_key(token),
        mapping={
            "id_usuario": str(usuario["_id"]),
            "email": usuario["email"],
            "alias": usuario["alias"],
            "rol": usuario.get("rol", "cliente"),
            "login_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    redis_client.expire(_session_key(token), SESSION_TTL)
    return token


def destruir_sesion(token: str) -> None:
    redis_client.delete(_session_key(token))


def usuario_actual(session_token: str | None = Cookie(default=None)) -> dict:
    """Dependencia: valida la cookie de sesión contra Redis y renueva el TTL (sliding)."""
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado: falta la sesión.",
        )

    datos = redis_client.hgetall(_session_key(session_token))
    if not datos:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada.",
        )

    # Renovamos el TTL en cada acceso para mantener viva la sesión activa.
    redis_client.expire(_session_key(session_token), SESSION_TTL)
    return datos


# --- Endpoints ---

@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioRegister):
    documento = {
        "email": datos.email.lower(),
        "password_hash": hash_password(datos.password),
        "alias": datos.alias,
        "rol": "cliente",
        "created_at": datetime.now(timezone.utc),
    }
    try:
        resultado = mongo_db.usuarios.insert_one(documento)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email.",
        )

    return UsuarioOut(
        id=str(resultado.inserted_id),
        email=documento["email"],
        alias=documento["alias"],
        rol=documento["rol"],
    )


@router.post("/login", response_model=UsuarioOut)
def login(datos: UsuarioLogin, response: Response):
    usuario = mongo_db.usuarios.find_one({"email": datos.email.lower()})
    if usuario is None or not verificar_password(datos.password, usuario.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    token = crear_sesion(usuario)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=None,
        secure=False,  # En producción (HTTPS) poner True.
        max_age=SESSION_TTL,
        path="/",
    )

    return UsuarioOut(
        id=str(usuario["_id"]),
        email=usuario["email"],
        alias=usuario["alias"],
        rol=usuario.get("rol", "cliente"),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, session_token: str | None = Cookie(default=None)):
    if session_token:
        destruir_sesion(session_token)
    response.delete_cookie(key=COOKIE_NAME, path="/")


@router.get("/me", response_model=UsuarioOut)
def perfil(sesion: dict = Depends(usuario_actual)):
    return UsuarioOut(
        id=sesion["id_usuario"],
        email=sesion["email"],
        alias=sesion["alias"],
        rol=sesion.get("rol", "cliente"),
    )
