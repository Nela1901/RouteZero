from sqlalchemy import text
from sqlalchemy.orm import Session


class RepositorioVehiculos:
    """Acceso a `vehiculos`, con SQL parametrizado (nunca interpolación de strings)."""

    def __init__(self, session: Session):
        self.session = session

    def existe_placa(self, placa: str) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM vehiculos WHERE placa = :placa"), {"placa": placa}
        ).one_or_none()
        return row is not None

    def crear(
        self,
        placa: str,
        tipo: str,
        capacidad_kg,
        consumo_km_l,
        factor_emision_co2,
        anio_fabricacion: int,
    ) -> str:
        row = self.session.execute(
            text(
                "INSERT INTO vehiculos "
                "(placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, \"año_fabricacion\") "
                "VALUES (:placa, :tipo, :capacidad_kg, :consumo_km_l, :factor_emision_co2, :anio) "
                "RETURNING vehiculo_id"
            ),
            {
                "placa": placa,
                "tipo": tipo,
                "capacidad_kg": capacidad_kg,
                "consumo_km_l": consumo_km_l,
                "factor_emision_co2": factor_emision_co2,
                "anio": anio_fabricacion,
            },
        ).one()
        return str(row[0])

    def obtener(self, vehiculo_id: str) -> dict | None:
        row = self.session.execute(
            text(
                "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, "
                "factor_emision_co2, \"año_fabricacion\", estado, creado_en "
                "FROM vehiculos WHERE vehiculo_id = :vid"
            ),
            {"vid": vehiculo_id},
        ).one_or_none()
        return self._a_dict(row) if row else None

    def actualizar(self, vehiculo_id: str, campos: dict) -> dict | None:
        if not campos:
            return self.obtener(vehiculo_id)
        columnas = {"anio_fabricacion": '"año_fabricacion"'}
        asignaciones = ", ".join(f"{columnas.get(c, c)} = :{c}" for c in campos)
        parametros = {**campos, "vid": vehiculo_id}
        row = self.session.execute(
            text(
                f"UPDATE vehiculos SET {asignaciones} WHERE vehiculo_id = :vid "
                "RETURNING vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, "
                "factor_emision_co2, \"año_fabricacion\", estado, creado_en"
            ),
            parametros,
        ).one_or_none()
        return self._a_dict(row) if row else None

    def listar(self, estado: str | None = None) -> list[dict]:
        if estado:
            rows = self.session.execute(
                text(
                    "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, "
                    "factor_emision_co2, \"año_fabricacion\", estado, creado_en "
                    "FROM vehiculos WHERE estado = :estado ORDER BY creado_en DESC"
                ),
                {"estado": estado},
            ).all()
        else:
            rows = self.session.execute(
                text(
                    "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, "
                    "factor_emision_co2, \"año_fabricacion\", estado, creado_en "
                    "FROM vehiculos ORDER BY creado_en DESC"
                )
            ).all()
        return [self._a_dict(r) for r in rows]

    @staticmethod
    def _a_dict(row) -> dict:
        return {
            "vehiculo_id": str(row[0]),
            "placa": row[1],
            "tipo": row[2],
            "capacidad_kg": row[3],
            "consumo_km_l": row[4],
            "factor_emision_co2": row[5],
            "anio_fabricacion": row[6],
            "estado": row[7],
            "creado_en": row[8],
        }
