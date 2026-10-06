from fastapi import HTTPException, status

from src.clientes.repository import RepositorioClientes
from src.core.zona import dentro_de_zona_cobertura


class ServicioClientes:
    def __init__(self, repo: RepositorioClientes):
        self.repo = repo

    def registrar(self, datos) -> dict:
        if self.repo.existe_nombre(datos.nombre):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un cliente con ese nombre")
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

    def obtener(self, cliente_id: str) -> dict:
        cliente = self.repo.obtener(cliente_id)
        if cliente is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
        return cliente

    def editar(self, cliente_id: str, datos) -> dict:
        campos = datos.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se envió ningún campo para actualizar")
        for obligatorio in ("nombre", "tipo_negocio", "latitud", "longitud", "horario_inicio", "horario_fin"):
            if obligatorio in campos and campos[obligatorio] is None:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY, f"El campo {obligatorio} no puede quedar vacío"
                )
        actual = self.obtener(cliente_id)
        if "nombre" in campos and self.repo.existe_nombre(campos["nombre"], excluir_id=cliente_id):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un cliente con ese nombre")
        latitud = campos.get("latitud", actual["latitud"])
        longitud = campos.get("longitud", actual["longitud"])
        if ("latitud" in campos or "longitud" in campos) and not dentro_de_zona_cobertura(latitud, longitud):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Las coordenadas están fuera del área de cobertura del distrito de Huancayo",
            )
        inicio = campos.get("horario_inicio", actual["horario_inicio"])
        fin = campos.get("horario_fin", actual["horario_fin"])
        if fin <= inicio:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "El horario de fin debe ser posterior al de inicio"
            )
        return self.repo.actualizar(cliente_id, campos)

    def eliminar(self, cliente_id: str) -> None:
        self.obtener(cliente_id)
        if self.repo.tiene_pedidos(cliente_id):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "El cliente tiene pedidos registrados y no se puede eliminar",
            )
        self.repo.eliminar(cliente_id)

    def listar(self) -> list[dict]:
        return self.repo.listar()
