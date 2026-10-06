from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(title="RouteZero API")

# Solo se acepta el origen exacto del frontend (variable de entorno), nunca "*". La API usa
# tokens en la cabecera Authorization, no cookies, así que no se habilitan credenciales.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(mfa_router)
app.include_router(sesiones_router)
app.include_router(flota_router)
app.include_router(conductores_router)
app.include_router(clientes_router)
app.include_router(pedidos_router)
app.include_router(rutas_router)
app.include_router(auditoria_router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(usuario: UsuarioActual = Depends(get_current_user)) -> dict:
    return {
        "usuario_id": usuario.usuario_id,
        "email": usuario.email,
        "rol_id": usuario.rol_id,
        "rol_nombre": usuario.rol_nombre,
        "mfa_activo": usuario.mfa_activo,
    }
