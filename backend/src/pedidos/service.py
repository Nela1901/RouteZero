from fastapi import HTTPException, status

from src.core.zona import dentro_de_zona_cobertura
from src.pedidos.repository import RepositorioPedidos


class ServicioPedidos:
    def __init__(self, repo: RepositorioPedidos):
        self.repo = repo

    def registrar(self, datos) -> dict:
        if not dentro_de_zona_cobertura(datos.latitud, datos.longitud):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Las coordenadas están fuera del área de cobertura del distrito de Huancayo",
            )
        if not self.repo.existe_cliente(datos.cliente_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")

        pedido_id = self.repo.crear(
            {
                "cliente_id": datos.cliente_id,
                "descripcion": datos.descripcion,
                "peso_kg": datos.peso_kg,
                "volumen_m3": datos.volumen_m3,
                "prioridad": datos.prioridad,
                "latitud": datos.latitud,
                "longitud": datos.longitud,
                "ventana_inicio": datos.ventana_inicio,
                "ventana_fin": datos.ventana_fin,
            }
        )
        return self.repo.obtener(pedido_id)

    def cancelar(self, pedido_id: str) -> dict:
        actual = self.repo.obtener(pedido_id)
        if actual is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
        actualizado = self.repo.cambiar_estado(pedido_id, "CANCELADO", desde_estados=["PENDIENTE"])
        if actualizado is None:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "El pedido ya fue asignado a una ruta; debe re-optimizarse la ruta para cancelarlo",
            )
        return actualizado

    def listar(self, estado: str | None, prioridad: str | None) -> list[dict]:
        return self.repo.listar(estado, prioridad)
