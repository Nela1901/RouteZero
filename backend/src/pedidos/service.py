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

    def obtener(self, pedido_id: str) -> dict:
        pedido = self.repo.obtener(pedido_id)
        if pedido is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
        return pedido

    def editar(self, pedido_id: str, datos) -> dict:
        campos = datos.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se envió ningún campo para actualizar")
        for obligatorio in ("cliente_id", "peso_kg", "prioridad", "latitud", "longitud", "ventana_inicio", "ventana_fin"):
            if obligatorio in campos and campos[obligatorio] is None:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY, f"El campo {obligatorio} no puede quedar vacío"
                )
        actual = self.obtener(pedido_id)
        if actual["estado"] != "PENDIENTE":
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Solo se puede editar un pedido pendiente; este ya fue asignado, entregado o cancelado",
            )
        if "cliente_id" in campos and not self.repo.existe_cliente(campos["cliente_id"]):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
        latitud = campos.get("latitud", actual["latitud"])
        longitud = campos.get("longitud", actual["longitud"])
        if ("latitud" in campos or "longitud" in campos) and not dentro_de_zona_cobertura(latitud, longitud):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Las coordenadas están fuera del área de cobertura del distrito de Huancayo",
            )
        inicio = campos.get("ventana_inicio", actual["ventana_inicio"])
        fin = campos.get("ventana_fin", actual["ventana_fin"])
        if fin <= inicio:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "La ventana de tiempo fin debe ser posterior al inicio"
            )
        actualizado = self.repo.actualizar(pedido_id, campos)
        if actualizado is None:
            # Cambió de estado entre la lectura y la escritura (p. ej. se confirmó una ruta).
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Solo se puede editar un pedido pendiente; este ya fue asignado, entregado o cancelado",
            )
        return actualizado

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

    def listar(self, estado: str | None, prioridad: str | None, limite: int, desplazamiento: int) -> dict:
        items, total = self.repo.listar(estado, prioridad, limite, desplazamiento)
        return {"items": items, "total": total, "limite": limite, "desplazamiento": desplazamiento}
