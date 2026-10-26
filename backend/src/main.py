from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import OperationalError

from src.auditoria.router import router as auditoria_router
from src.auth.router import router as mfa_router
from src.auth.router_sesiones import router as sesiones_router
from src.clientes.router import router as clientes_router
from src.conductores.router import router as conductores_router
from src.core.config import settings
from src.core.security import UsuarioActual, get_current_user
from src.flota.router import router as flota_router
from src.pedidos.router import router as pedidos_router
from src.rutas.router import router as rutas_router
from src.sostenibilidad.router import router as sostenibilidad_router

app = FastAPI(title="RouteZero API")

# Solo se acepta el origen exacto del frontend (variable de entorno), nunca "*". La API usa
# tokens en la cabecera Authorization, no cookies, así que no se habilitan credenciales.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # PATCH: registrar entregas (HU-014)
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def cabeceras_de_seguridad(request: Request, call_next):
    """OWASP A02: cabeceras que endurecen toda respuesta y evitan que el navegador o un intermediario guarde datos de la API."""
    respuesta = await call_next(request)
    respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
    respuesta.headers.setdefault("X-Frame-Options", "DENY")
    respuesta.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.url.path.startswith("/api/"):
        respuesta.headers.setdefault("Cache-Control", "no-store")
    return respuesta


@app.exception_handler(httpx.RequestError)
async def servicio_externo_no_responde(request: Request, exc: httpx.RequestError) -> JSONResponse:
    """OWASP A10: si Supabase no responde o se corta la conexión, se contesta 503 con un mensaje claro y no un 500 genérico."""
    return JSONResponse(status_code=503, content={"detail": "Un servicio externo no responde. Inténtalo de nuevo en unos minutos."})


@app.exception_handler(OperationalError)
async def base_de_datos_no_disponible(request: Request, exc: OperationalError) -> JSONResponse:
    """OWASP A10: la base de datos caída o saturada responde 503, sin exponer el detalle de la conexión."""
    return JSONResponse(status_code=503, content={"detail": "La base de datos no está disponible. Inténtalo de nuevo en unos minutos."})


app.include_router(mfa_router)
app.include_router(sesiones_router)
app.include_router(flota_router)
app.include_router(conductores_router)
app.include_router(clientes_router)
app.include_router(pedidos_router)
app.include_router(rutas_router)
app.include_router(sostenibilidad_router)
app.include_router(auditoria_router)


@app.get("/", include_in_schema=False)
def raiz() -> RedirectResponse:
    """La URL pública del backend lleva a la documentación interactiva en vez de a un 404."""
    return RedirectResponse("/docs")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(usuario: Annotated[UsuarioActual, Depends(get_current_user)]) -> dict:
    return {
        "usuario_id": usuario.usuario_id,
        "email": usuario.email,
        "rol_id": usuario.rol_id,
        "rol_nombre": usuario.rol_nombre,
        "mfa_activo": usuario.mfa_activo,
    }
