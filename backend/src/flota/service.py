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
        if "placa" in campos:
            if campos["placa"] is None:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La placa no puede quedar vacía")
            if self.repo.existe_placa(campos["placa"], excluir_id=vehiculo_id):
                raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un vehículo con esa placa")
        actualizado = self.repo.actualizar(vehiculo_id, campos)
        if actualizado is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
        return actualizado

    def obtener(self, vehiculo_id: str) -> dict:
        vehiculo = self.repo.obtener(vehiculo_id)
        if vehiculo is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
        return vehiculo

    def eliminar(self, vehiculo_id: str) -> None:
        self.obtener(vehiculo_id)
        if self.repo.tiene_rutas(vehiculo_id):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "El vehículo tiene rutas registradas y no se puede eliminar; márcalo como INACTIVO para dejar de usarlo",
            )
        self.repo.eliminar(vehiculo_id)

    def listar(self, estado: str | None) -> list[dict]:
        return self.repo.listar(estado)
