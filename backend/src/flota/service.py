from fastapi import HTTPException, status

from src.flota.repository import RepositorioVehiculos


class ServicioVehiculos:
    def __init__(self, repo: RepositorioVehiculos):
        self.repo = repo

    def registrar(self, datos) -> dict:
        if self.repo.existe_placa(datos.placa):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un vehículo con esa placa")
        vehiculo_id = self.repo.crear(
            datos.placa,
            datos.tipo,
            datos.capacidad_kg,
            datos.consumo_km_l,
            datos.factor_emision_co2,
            datos.anio_fabricacion,
            datos.soat_vence,
            datos.revision_tecnica_vence,
        )
        return self.repo.obtener(vehiculo_id)

    def editar(self, vehiculo_id: str, datos) -> dict:
        campos = datos.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se envió ningún campo para actualizar")
        actualizado = self.repo.actualizar(vehiculo_id, campos)
        if actualizado is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
        return actualizado

    def listar(self, estado: str | None) -> list[dict]:
        return self.repo.listar(estado)
