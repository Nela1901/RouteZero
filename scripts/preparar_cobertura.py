"""Deja los reportes de cobertura con rutas relativas a la raíz del repositorio, que es lo que SonarQube espera.

pytest-cov y Vitest generan rutas relativas a sus propias carpetas (`src/auth/...` dentro de `backend/`, `src/api/...`
dentro de `frontend/`) y, en Windows, con barras invertidas. SonarQube resuelve las rutas desde la raíz del proyecto,
así que sin este paso no encuentra los archivos y muestra la cobertura en 0.

Uso, desde la raíz del repositorio (después de generar los reportes):
    python scripts/preparar_cobertura.py
"""

import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
XML_BACKEND = RAIZ / "backend" / "coverage.xml"
LCOV_FRONTEND = RAIZ / "frontend" / "coverage" / "lcov.info"


def _con_prefijo(ruta: str, prefijo: str) -> str:
    ruta = ruta.replace("\\", "/")
    return ruta if ruta.startswith(prefijo + "/") else f"{prefijo}/{ruta}"


def preparar_backend() -> int:
    if not XML_BACKEND.exists():
        print(f"No existe {XML_BACKEND.relative_to(RAIZ)}: ejecuta antes pytest (ver el documento de calidad de código).")
        return 0
    arbol = ET.parse(XML_BACKEND)
    raiz = arbol.getroot()
    for fuentes in raiz.iter("sources"):
        fuentes.clear()
        ET.SubElement(fuentes, "source").text = "."
    archivos = 0
    for clase in raiz.iter("class"):
        clase.set("filename", _con_prefijo(clase.get("filename", ""), "backend"))
        archivos += 1
    arbol.write(XML_BACKEND, encoding="utf-8", xml_declaration=True)
    return archivos


def preparar_frontend() -> int:
    if not LCOV_FRONTEND.exists():
        print(f"No existe {LCOV_FRONTEND.relative_to(RAIZ)}: ejecuta antes `npm run test:coverage` en frontend/.")
        return 0
    lineas, archivos = [], 0
    for linea in LCOV_FRONTEND.read_text(encoding="utf-8").splitlines():
        if linea.startswith("SF:"):
            linea = "SF:" + _con_prefijo(linea[3:], "frontend")
            archivos += 1
        lineas.append(linea)
    LCOV_FRONTEND.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return archivos


if __name__ == "__main__":
    print(f"backend/coverage.xml: {preparar_backend()} archivos con rutas desde la raíz")
    print(f"frontend/coverage/lcov.info: {preparar_frontend()} archivos con rutas desde la raíz")
