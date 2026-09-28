from datetime import datetime

from pydantic import BaseModel


class LogAuditoriaOut(BaseModel):
    log_id: str
    usuario_id: str | None
    accion: str
    modulo: str
    detalle: str | None
    ip_origen: str | None
    creado_en: datetime
