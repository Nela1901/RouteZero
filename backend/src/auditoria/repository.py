from sqlalchemy import text
from sqlalchemy.orm import Session

MAX_DETALLE = 2000

_COLUMNAS = "log_id, usuario_id, accion, modulo, detalle, ip_origen, creado_en"


class RepositorioAuditoria:
    """Acceso a `logs_auditoria`, vía SQL parametrizado. `registrar` nunca hace `commit()`
    (misma convención que el resto de repositorios): queda en la transacción de la petición
    que disparó el evento, así un rollback también deshace el registro de auditoría."""

    def __init__(self, session: Session):
        self.session = session

    def registrar(
        self,
        usuario_id: str | None,
        accion: str,
        modulo: str,
        detalle: str | None = None,
        ip_origen: str | None = None,
    ) -> None:
        self.session.execute(
            text(
                "INSERT INTO logs_auditoria (usuario_id, accion, modulo, detalle, ip_origen) "
                "VALUES (:uid, :accion, :modulo, :detalle, :ip)"
            ),
            {
                "uid": usuario_id,
                "accion": accion,
                "modulo": modulo,
                "detalle": (detalle or None) and detalle[:MAX_DETALLE],
                "ip": ip_origen,
            },
        )

    def listar(self, modulo: str | None, limite: int) -> list[dict]:
        condicion = "WHERE modulo = :modulo " if modulo else ""
        rows = self.session.execute(
            text(
                f"SELECT {_COLUMNAS} FROM logs_auditoria {condicion}"
                "ORDER BY creado_en DESC LIMIT :limite"
            ),
            {"modulo": modulo, "limite": limite},
        ).all()
        registros = []
        for r in rows:
            fila = dict(r._mapping)
            fila["log_id"] = str(fila["log_id"])
            fila["usuario_id"] = str(fila["usuario_id"]) if fila["usuario_id"] is not None else None
            registros.append(fila)
        return registros
