"""Independencia de módulos (HT-08, spec `api-scalability`): ningún módulo de negocio importa a otro
(salvo `core` y `auditoria`), y el motor `algoritmo` no depende de FastAPI, SQLAlchemy ni del backend.

Analiza el código con `ast`, sin ejecutarlo ni tocar la base de datos.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

NEGOCIO = {"auth", "flota", "conductores", "clientes", "pedidos", "rutas"}
COMPARTIDOS = {"core", "auditoria"}
# Módulos que `rutas` puede usar además de los compartidos: el motor y la red vial.
PERMITIDOS_POR_MODULO = {"rutas": {"red_vial", "algoritmo"}}
LIBRERIAS_PROHIBIDAS_EN_ALGORITMO = {"fastapi", "starlette", "sqlalchemy", "psycopg2", "pydantic", "jwt"}


def modulos_importados(codigo: str) -> set[str]:
    """Nombres de los módulos importados, p. ej. {'src.core.security', 'fastapi'}."""
    encontrados: set[str] = set()
    for nodo in ast.walk(ast.parse(codigo)):
        if isinstance(nodo, ast.Import):
            encontrados.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
            encontrados.add(nodo.module)
    return encontrados


def paquete_de_src(modulo: str) -> str | None:
    """'src.pedidos.service' -> 'pedidos'; cualquier otro nombre -> None."""
    partes = modulo.split(".")
    return partes[1] if partes[0] == "src" and len(partes) > 1 else None


def violaciones(paquete: str, codigo: str) -> list[str]:
    """Importaciones prohibidas de un archivo que pertenece a `paquete`."""
    malas = []
    for modulo in sorted(modulos_importados(codigo)):
        if paquete == "algoritmo":
            raiz = modulo.split(".")[0]
            if raiz in LIBRERIAS_PROHIBIDAS_EN_ALGORITMO or (raiz == "src" and paquete_de_src(modulo) != "algoritmo"):
                malas.append(modulo)
            continue
        destino = paquete_de_src(modulo)
        if destino is None or destino == paquete or destino in COMPARTIDOS:
            continue
        if paquete in NEGOCIO and destino not in PERMITIDOS_POR_MODULO.get(paquete, set()):
            malas.append(modulo)
        elif paquete in COMPARTIDOS and destino not in {"core"}:
            malas.append(modulo)
    return malas


def archivos_por_paquete():
    for archivo in sorted(SRC.rglob("*.py")):
        relativo = archivo.relative_to(SRC)
        if len(relativo.parts) > 1:  # main.py, en la raíz, es la composición de la aplicación
            yield relativo.parts[0], archivo


def test_ningun_modulo_importa_a_otro_modulo_de_negocio():
    problemas = {}
    for paquete, archivo in archivos_por_paquete():
        malas = violaciones(paquete, archivo.read_text(encoding="utf-8"))
        if malas:
            problemas[str(archivo.relative_to(SRC))] = malas
    assert not problemas, f"Dependencias prohibidas entre módulos: {problemas}"


def test_el_detector_encuentra_una_dependencia_prohibida_entre_modulos():
    assert violaciones("pedidos", "from src.clientes.repository import RepositorioClientes") == [
        "src.clientes.repository"
    ]


def test_el_detector_permite_core_y_auditoria():
    codigo = "from src.core.security import requiere_rol\nfrom src.auditoria.repository import RepositorioAuditoria"
    assert violaciones("conductores", codigo) == []


def test_el_detector_permite_a_rutas_usar_el_motor_y_la_red_vial():
    assert violaciones("rutas", "from src.algoritmo.aco import resolver\nfrom src.red_vial.matrices import calcular") == []


def test_el_detector_rechaza_librerias_de_infraestructura_en_el_algoritmo():
    codigo = "import numpy\nfrom fastapi import HTTPException\nfrom sqlalchemy import text\nfrom src.core.config import settings"
    assert violaciones("algoritmo", codigo) == ["fastapi", "sqlalchemy", "src.core.config"]


def test_el_algoritmo_puede_importar_sus_propios_modulos_y_numpy():
    assert violaciones("algoritmo", "import numpy as np\nfrom src.algoritmo.modelo import Problema") == []
