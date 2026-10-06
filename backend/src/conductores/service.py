from datetime import date, datetime

from fastapi import HTTPException, status

from src.auditoria.repository import RepositorioAuditoria
from src.conductores.repository import RepositorioConductores

# Ley N° 30224 / RN-002: la jornada de un conductor no excede las 8 horas.
JORNADA_MAXIMA_HORAS = 8


def _validar_jornada(horario_inicio, horario_fin) -> None:
    if horario_fin <= horario_inicio:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "El horario de fin debe ser posterior al de inicio"
        )
    horas = (
        datetime.combine(date.min, horario_fin) - datetime.combine(date.min, horario_inicio)
    ).total_seconds() / 3600
    if horas > JORNADA_MAXIMA_HORAS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"La disponibilidad horaria no puede superar la jornada máxima de {JORNADA_MAXIMA_HORAS} horas",
        )


def _validar_licencia_vigente(licencia_vence: date) -> None:
    if licencia_vence <= date.today():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "La licencia está vencida o vence hoy; la fecha de vencimiento debe ser posterior a hoy",
        )


class ServicioConductores:
    def __init__(self, repo: RepositorioConductores):
        self.repo = repo
        self.auditoria = RepositorioAuditoria(repo.session)

    def registrar(self, datos, usuario_id: str) -> dict:
        if self.repo.existe_dni(datos.dni):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un conductor con ese DNI")
        _validar_jornada(datos.horario_inicio, datos.horario_fin)
        _validar_licencia_vigente(datos.licencia_vence)
        conductor_id = self.repo.crear(
            datos.nombre,
            datos.dni,
            datos.categoria_licencia,
            datos.telefono,
            datos.correo,
            datos.licencia_vence,
            datos.horario_inicio,
            datos.horario_fin,
        )
        # El DNI es dato personal (Ley N° 29733): el registro de auditoría guarda solo el id.
        self.auditoria.registrar(usuario_id, "conductor_registrado", "conductores", conductor_id)
        return self.repo.obtener(conductor_id)

    def editar(self, conductor_id: str, datos, usuario_id: str) -> dict:
        campos = datos.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se envió ningún campo para actualizar")
        if campos.get("licencia_vence"):
            _validar_licencia_vigente(campos["licencia_vence"])
        actual = self.repo.obtener(conductor_id)
        if actual is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
        if "horario_inicio" in campos or "horario_fin" in campos:
            _validar_jornada(
                campos.get("horario_inicio") or actual["horario_inicio"],
                campos.get("horario_fin") or actual["horario_fin"],
            )
        actualizado = self.repo.actualizar(conductor_id, campos)
        self.auditoria.registrar(usuario_id, "conductor_editado", "conductores", conductor_id)
        return actualizado

    def listar(self, disponible: bool | None) -> list[dict]:
        return self.repo.listar(disponible)
