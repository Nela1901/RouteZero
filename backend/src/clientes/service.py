from fastapi import HTTPException, status

from src.clientes.repository import RepositorioClientes
from src.clientes.zona import dentro_de_zona_cobertura


class ServicioClientes:
    def __init__(self, repo: RepositorioClientes):
        self.repo = repo

    def registrar(self, datos) -> dict:
        if not dentro_de_zona_cobertura(datos.latitud, datos.longitud):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Las coordenadas están fuera del área de cobertura del distrito de Huancayo",
            )
        cliente_id = self.repo.crear(
            datos.nombre,
            datos.tipo_negocio,
            datos.referencia,
            datos.latitud,
            datos.longitud,
            datos.horario_inicio,
            datos.horario_fin,
        )
        return self.repo.obtener(cliente_id)

    def listar(self) -> list[dict]:
        return self.repo.listar()
