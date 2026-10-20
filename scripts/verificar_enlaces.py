"""Verifica los enlaces de todos los documentos Markdown del repositorio (solo lectura).

Comprueba, para cada .md versionado:
  - que cada enlace relativo (a un archivo, carpeta o imagen) llegue a algo que existe;
  - que cada enlace a una sección (#ancla) tenga su encabezado;
  - que cada documento de docs/ tenga su enlace de retorno al README.md.

Uso, desde la raíz del repositorio:  python scripts/verificar_enlaces.py
Termina con código 1 si encuentra algún problema, para poder usarlo antes de un Pull Request.
"""

import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]


def git(*args: str) -> list[str]:
    salida = subprocess.run(["git", "-c", "core.quotepath=false", *args], capture_output=True, cwd=RAIZ)
    return salida.stdout.decode("utf-8", "replace").splitlines()


archivos = set(git("ls-files")) | set(git("ls-files", "--others", "--exclude-standard"))
carpetas: set[str] = set()
for a in archivos:
    p = posixpath.dirname(a)
    while p:
        carpetas.add(p)
        p = posixpath.dirname(p)

documentos = sorted(a for a in archivos if a.endswith(".md"))
ENLACE = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def leer(ruta: str) -> str:
    cuerpo = (RAIZ / ruta).read_text(encoding="utf-8")
    return re.sub(r"```.*?```", "", cuerpo, flags=re.S)  # los bloques de código no cuentan


def identificador(titulo: str) -> str:
    """Ancla que GitHub genera para un encabezado."""
    texto = re.sub(r"[*_`]|<[^>]+>", "", titulo).strip().lower()
    return re.sub(r"[^\w\- ]", "", texto).replace(" ", "-")


def anclas(ruta: str) -> set[str]:
    vistos: dict[str, int] = {}
    resultado = set()
    for encabezado in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", leer(ruta), flags=re.M):
        base = identificador(encabezado)
        n = vistos.get(base, 0)
        resultado.add(base if n == 0 else f"{base}-{n}")
        vistos[base] = n + 1
    return resultado


problemas: list[str] = []
total = 0
cache_anclas: dict[str, set[str]] = {}

for doc in documentos:
    for _texto, destino in ENLACE.findall(leer(doc)):
        if re.match(r"^(https?:|mailto:|tel:|data:)", destino):
            continue
        total += 1
        ruta, _, ancla = destino.partition("#")
        objetivo = doc if not ruta else posixpath.normpath(posixpath.join(posixpath.dirname(doc), unquote(ruta)))
        if objetivo not in archivos and objetivo not in carpetas:
            problemas.append(f"{doc}\n    enlace roto: {unquote(destino)}")
            continue
        if ancla and objetivo.endswith(".md"):
            cache_anclas.setdefault(objetivo, anclas(objetivo))
            if unquote(ancla).lower() not in cache_anclas[objetivo]:
                problemas.append(f"{doc}\n    sección inexistente: {unquote(destino)}")

    if doc.startswith("docs/"):
        retornos = re.findall(r"\[[^\]]*README[^\]]*\]\(([^)\s]+)\)", leer(doc))
        if not any(posixpath.normpath(posixpath.join(posixpath.dirname(doc), unquote(r))) == "README.md" for r in retornos):
            problemas.append(f"{doc}\n    falta el enlace de retorno al README.md")

print(f"{len(documentos)} documentos, {total} enlaces relativos revisados")
if problemas:
    print(f"\n{len(problemas)} problema(s):")
    print("\n".join(problemas))
    sys.exit(1)
print("Sin enlaces rotos.")
