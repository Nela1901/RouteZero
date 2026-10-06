from sqlalchemy import text
from sqlalchemy.orm import Session

_COLUMNAS = (
    "conductor_id, nombre, dni, categoria_licencia, telefono, correo, licencia_vence, "
    "horario_inicio, horario_fin, "
    "disponible, horas_conducidas_hoy, consentimiento_en, creado_en"
)

# Solo estas columnas se pueden actualizar; nunca se interpola un nombre que venga del cliente.
_ACTUALIZABLES = {"categoria_licencia", "telefono", "correo", "licencia_vence", "horario_inicio", "horario_fin", "disponible"}


class RepositorioConductores:
    """Acceso a `conductores`, con SQL parametrizado (nunca interpolación de strings)."""

    def __init__(self, session: Session):
        self.session = session

    def existe_dni(self, dni: str) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM conductores WHERE dni = :dni"), {"dni": dni}
        ).one_or_none()
        return row is not None

    def crear(
        self,
        nombre: str,
        dni: str,
        categoria_licencia: str,
        telefono: str,
        correo: str | None,
        licencia_vence,
        horario_inicio,
        horario_fin,
    ) -> str:
        row = self.session.execute(
            text(
                "INSERT INTO conductores "
                "(nombre, dni, categoria_licencia, telefono, correo, licencia_vence, horario_inicio, horario_fin, "
                "consentimiento_datos, consentimiento_en) "
                "VALUES (:nombre, :dni, :categoria, :telefono, :correo, :vence, :hi, :hf, TRUE, now()) "
                "RETURNING conductor_id"
            ),
            {
                "nombre": nombre,
                "dni": dni,
                "categoria": categoria_licencia,
                "telefono": telefono,
                "correo": correo,
                "vence": licencia_vence,
                "hi": horario_inicio,
                "hf": horario_fin,
            },
        ).one()
        return str(row[0])

    def obtener(self, conductor_id: str) -> dict | None:
        row = self.session.execute(
            text(f"SELECT {_COLUMNAS} FROM conductores WHERE conductor_id = :cid"),
            {"cid": conductor_id},
        ).one_or_none()
        return self._a_dict(row) if row else None

    def actualizar(self, conductor_id: str, campos: dict) -> dict | None:
        campos = {c: v for c, v in campos.items() if c in _ACTUALIZABLES}
        if not campos:
            return self.obtener(conductor_id)
        asignaciones = ", ".join(f"{c} = :{c}" for c in campos)
        row = self.session.execute(
            text(
                f"UPDATE conductores SET {asignaciones} WHERE conductor_id = :cid "
                f"RETURNING {_COLUMNAS}"
            ),
            {**campos, "cid": conductor_id},
        ).one_or_none()
        return self._a_dict(row) if row else None

    def listar(self, disponible: bool | None = None) -> list[dict]:
        if disponible is None:
            rows = self.session.execute(
                text(f"SELECT {_COLUMNAS} FROM conductores ORDER BY creado_en DESC")
            ).all()
        else:
            rows = self.session.execute(
                text(
                    f"SELECT {_COLUMNAS} FROM conductores WHERE disponible = :d "
                    "ORDER BY creado_en DESC"
                ),
                {"d": disponible},
            ).all()
        return [self._a_dict(r) for r in rows]

    @staticmethod
    def _a_dict(row) -> dict:
        return {
            "conductor_id": str(row[0]),
            "nombre": row[1],
            "dni": row[2],
            "categoria_licencia": row[3],
            "telefono": row[4],
            "correo": row[5],
            "licencia_vence": row[6],
            "horario_inicio": row[7],
            "horario_fin": row[8],
            "disponible": row[9],
            "horas_conducidas_hoy": row[10],
            "consentimiento_en": row[11],
            "creado_en": row[12],
        }
