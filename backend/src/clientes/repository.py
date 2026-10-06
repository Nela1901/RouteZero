from sqlalchemy import text
from sqlalchemy.orm import Session


class RepositorioClientes:
    def __init__(self, session: Session):
        self.session = session

    def crear(
        self,
        nombre: str,
        tipo_negocio: str,
        referencia: str | None,
        latitud,
        longitud,
        horario_inicio,
        horario_fin,
    ) -> str:
        row = self.session.execute(
            text(
                "INSERT INTO clientes "
                "(nombre, tipo_negocio, referencia, latitud, longitud, horario_inicio, horario_fin) "
                "VALUES (:nombre, :tipo, :referencia, :lat, :lon, :hi, :hf) "
                "RETURNING cliente_id"
            ),
            {
                "nombre": nombre,
                "tipo": tipo_negocio,
                "referencia": referencia,
                "lat": latitud,
                "lon": longitud,
                "hi": horario_inicio,
                "hf": horario_fin,
            },
        ).one()
        return str(row[0])

    def obtener(self, cliente_id: str) -> dict | None:
        row = self.session.execute(
            text(
                "SELECT cliente_id, nombre, tipo_negocio, referencia, latitud, longitud, "
                "horario_inicio, horario_fin, creado_en FROM clientes WHERE cliente_id = :cid"
            ),
            {"cid": cliente_id},
        ).one_or_none()
        return self._a_dict(row) if row else None

    def existe_nombre(self, nombre: str) -> bool:
        """Comparación sin distinguir mayúsculas: "Bodega Sol" y "bodega sol" son el mismo cliente."""
        row = self.session.execute(
            text("SELECT 1 FROM clientes WHERE lower(nombre) = lower(:nombre)"), {"nombre": nombre}
        ).one_or_none()
        return row is not None

    def listar(self) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT cliente_id, nombre, tipo_negocio, referencia, latitud, longitud, "
                "horario_inicio, horario_fin, creado_en FROM clientes ORDER BY creado_en DESC"
            )
        ).all()
        return [self._a_dict(r) for r in rows]

    @staticmethod
    def _a_dict(row) -> dict:
        return {
            "cliente_id": str(row[0]),
            "nombre": row[1],
            "tipo_negocio": row[2],
            "referencia": row[3],
            "latitud": row[4],
            "longitud": row[5],
            "horario_inicio": row[6],
            "horario_fin": row[7],
            "creado_en": row[8],
        }
