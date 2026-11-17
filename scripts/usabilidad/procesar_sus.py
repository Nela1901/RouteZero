"""Procesamiento de las respuestas de la escala SUS (System Usability Scale).

Lee el CSV que exporta Google Forms (Respuestas > Descargar respuestas .csv), valida las respuestas, calcula el
puntaje de cada participante paso a paso, el promedio global y su clasificación, y escribe un informe en Markdown (y, si
`matplotlib` está instalado, dos gráficos en PNG). Solo usa la biblioteca estándar de Python.

Uso (desde la raíz del repositorio):
    python scripts/usabilidad/procesar_sus.py respuestas.csv --salida resultados_sus

El CSV no se versiona ni se modifica. Los participantes se numeran P01, P02... por el orden de las filas: nunca se
usan nombres ni correos.

Cálculo (Brooke, 1996): ítems impares (1, 3, 5, 7, 9): contribución = respuesta - 1. Ítems pares (2, 4, 6, 8, 10):
contribución = 5 - respuesta. Puntaje = suma de las 10 contribuciones x 2,5 (rango de 0 a 100).
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

UMBRAL_ACEPTACION = 68.0  # media de la industria; la consigna exige >= 68
MUESTRA_MINIMA = 5  # la rúbrica pide n >= 5

# Grado de letra según la escala «curved grading» de Sauro y Lewis (2016, Quantifying the User Experience, 2.ª ed.).
# Verifica los cortes con la fuente antes de citarlos en el informe.
GRADOS = [
    (84.1, "A+"), (80.8, "A"), (78.9, "A-"), (77.2, "B+"), (74.1, "B"), (72.6, "B-"),
    (71.1, "C+"), (65.0, "C"), (62.7, "C-"), (51.7, "D"), (0.0, "F"),
]
# Adjetivo según Bangor, Kortum y Miller (2009). Se usa el adjetivo cuya media de referencia queda más cerca.
ADJETIVOS = [
    (12.5, "el peor imaginable"), (20.3, "pésimo"), (35.7, "malo"), (50.9, "regular"),
    (71.4, "bueno"), (85.5, "excelente"), (90.9, "el mejor imaginable"),
]


@dataclass
class Participante:
    codigo: str
    respuestas: list[int]  # P1..P10
    contexto: dict[str, str]

    @property
    def contribuciones(self) -> list[int]:
        return contribuciones(self.respuestas)

    @property
    def puntaje(self) -> float:
        return puntaje(self.respuestas)


def contribuciones(respuestas: list[int]) -> list[int]:
    """Contribución (0 a 4) de cada ítem: impares, respuesta - 1; pares, 5 - respuesta."""
    if len(respuestas) != 10:
        raise ValueError(f"La SUS tiene 10 ítems; llegaron {len(respuestas)}.")
    for i, valor in enumerate(respuestas, start=1):
        if valor not in (1, 2, 3, 4, 5):
            raise ValueError(f"El ítem {i} debe estar entre 1 y 5; llegó {valor!r}.")
    return [valor - 1 if i % 2 == 1 else 5 - valor for i, valor in enumerate(respuestas, start=1)]


def puntaje(respuestas: list[int]) -> float:
    return sum(contribuciones(respuestas)) * 2.5


def grado(valor: float) -> str:
    return next(letra for corte, letra in GRADOS if valor >= corte)


def adjetivo(valor: float) -> str:
    return min(ADJETIVOS, key=lambda par: abs(par[0] - valor))[1]


def leer_csv(ruta: Path) -> list[Participante]:
    contenido = ruta.read_text(encoding="utf-8-sig")
    try:
        dialecto = csv.Sniffer().sniff(contenido[:2000], delimiters=",;\t")
    except csv.Error:
        dialecto = csv.excel
    filas = list(csv.DictReader(contenido.splitlines(), dialect=dialecto))
    if not filas:
        raise ValueError("El archivo no tiene respuestas.")

    # Las columnas de la SUS son las que empiezan por «P1.» ... «P10.» (así las titula el formulario).
    columnas_sus: dict[int, str] = {}
    for nombre in filas[0]:
        encontrado = re.match(r"^\s*P(\d{1,2})\s*[.\-:)]", nombre or "")
        if encontrado and 1 <= int(encontrado.group(1)) <= 10:
            columnas_sus[int(encontrado.group(1))] = nombre
    faltan = [n for n in range(1, 11) if n not in columnas_sus]
    if faltan:
        raise ValueError(f"No encuentro las columnas de los ítems {faltan}. Deben empezar por «P1.», «P2.»...")
    columnas_contexto = [
        n for n in filas[0]
        if n and n not in columnas_sus.values() and "marca temporal" not in n.lower() and "timestamp" not in n.lower()
        and not n.lower().startswith(("¿qué fue lo que más", "¿qué cambiarías"))
    ]

    participantes: list[Participante] = []
    for numero, fila in enumerate(filas, start=1):
        codigo = f"P{numero:02d}"
        try:
            respuestas = [int(str(fila[columnas_sus[i]]).strip()) for i in range(1, 11)]
            contribuciones(respuestas)  # valida el rango
        except (ValueError, TypeError) as error:
            raise ValueError(f"Fila {numero} ({codigo}) inválida: {error}") from error
        participantes.append(
            Participante(codigo, respuestas, {c: (fila.get(c) or "").strip() for c in columnas_contexto})
        )
    return participantes


def _fmt(valor: float) -> str:
    return f"{valor:.1f}".rstrip("0").rstrip(".") if valor != int(valor) else f"{int(valor)}"


def informe(participantes: list[Participante]) -> str:
    n = len(participantes)
    puntajes = [p.puntaje for p in participantes]
    media = statistics.fmean(puntajes)
    desviacion = statistics.stdev(puntajes) if n > 1 else 0.0
    lineas: list[str] = ["# Resultados de la escala SUS", ""]

    lineas += ["## Resumen", "", "| Indicador | Valor |", "|---|---|"]
    lineas += [
        f"| Participantes (n) | {n} |",
        f"| Puntaje SUS promedio | **{media:.1f}** |",
        f"| Desviación estándar | {desviacion:.1f} |",
        f"| Mediana | {_fmt(statistics.median(puntajes))} |",
        f"| Mínimo / máximo | {_fmt(min(puntajes))} / {_fmt(max(puntajes))} |",
        f"| Umbral de aceptación | {_fmt(UMBRAL_ACEPTACION)} |",
        f"| ¿Alcanza el umbral (>= {_fmt(UMBRAL_ACEPTACION)})? | {'Sí' if media >= UMBRAL_ACEPTACION else 'No'} |",
        f"| Grado (Sauro y Lewis) | {grado(media)} |",
        f"| Adjetivo (Bangor et al.) | {adjetivo(media)} |",
        f"| Participantes bajo el umbral | {sum(1 for v in puntajes if v < UMBRAL_ACEPTACION)} de {n} |",
        "",
    ]
    if n < MUESTRA_MINIMA:
        lineas += [f"> **Aviso:** n = {n} es menor que {MUESTRA_MINIMA}, el mínimo que pide la rúbrica.", ""]

    lineas += ["## Respuestas brutas por participante", "", "| Participante | " + " | ".join(f"P{i}" for i in range(1, 11)) + " |"]
    lineas += ["|---|" + "---|" * 10]
    lineas += [f"| {p.codigo} | " + " | ".join(str(v) for v in p.respuestas) + " |" for p in participantes]
    lineas += [""]

    lineas += [
        "## Cálculo paso a paso por participante",
        "",
        "Impares (P1, P3, P5, P7, P9): contribución = respuesta - 1. Pares (P2, P4, P6, P8, P10): contribución = 5 - respuesta.",
        "Puntaje = suma de contribuciones x 2,5.",
        "",
        "| Participante | " + " | ".join(f"P{i}" for i in range(1, 11)) + " | Suma | Puntaje (x 2,5) |",
        "|---|" + "---|" * 12,
    ]
    for p in participantes:
        contrib = p.contribuciones
        lineas.append(f"| {p.codigo} | " + " | ".join(str(c) for c in contrib) + f" | {sum(contrib)} | {_fmt(p.puntaje)} |")
    lineas += ["", f"**Promedio global:** ({' + '.join(_fmt(v) for v in puntajes)}) / {n} = **{media:.1f}**", ""]

    lineas += ["## Promedio por ítem (contribución de 0 a 4)", "", "| Ítem | Enunciado | Contribución media | Respuesta media |", "|---|---|---|---|"]
    enunciados = [
        "Me gustaría usarlo con regularidad", "Es innecesariamente complejo", "Es fácil de usar",
        "Necesitaría ayuda de una persona con experiencia", "Las funciones están bien integradas",
        "Hay demasiada inconsistencia", "La mayoría aprendería a usarlo muy rápido",
        "Es muy complicado de usar", "Me siento confiado usándolo", "Necesitaría aprender muchas cosas antes",
    ]
    medias_item = []
    for i in range(10):
        contribucion = statistics.fmean(p.contribuciones[i] for p in participantes)
        respuesta = statistics.fmean(p.respuestas[i] for p in participantes)
        medias_item.append(contribucion)
        lineas.append(f"| P{i + 1} | {enunciados[i]} | {contribucion:.2f} | {respuesta:.2f} |")
    peor = sorted(range(10), key=lambda i: medias_item[i])[:3]
    lineas += ["", "Los tres ítems con menor contribución (los puntos más débiles percibidos): "
               + ", ".join(f"P{i + 1} ({medias_item[i]:.2f})" for i in peor) + ".", ""]

    # Desglose por columnas de contexto (rol, dispositivo, experiencia).
    contextos = sorted({c for p in participantes for c in p.contexto})
    for columna in contextos:
        grupos: dict[str, list[float]] = {}
        for p in participantes:
            grupos.setdefault(p.contexto.get(columna) or "(sin dato)", []).append(p.puntaje)
        lineas += [f"## Puntaje por: {columna}", "", "| Grupo | n | Promedio SUS |", "|---|---|---|"]
        lineas += [f"| {g} | {len(v)} | {statistics.fmean(v):.1f} |" for g, v in sorted(grupos.items())]
        lineas += [""]
    return "\n".join(lineas) + "\n"


def graficos(participantes: list[Participante], carpeta: Path) -> list[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []
    creados: list[Path] = []
    puntajes = [p.puntaje for p in participantes]
    media = statistics.fmean(puntajes)

    figura, eje = plt.subplots(figsize=(8, 4.5))
    barras = eje.bar([p.codigo for p in participantes], puntajes, color="#2f6fa3")
    eje.axhline(UMBRAL_ACEPTACION, color="#c0392b", linestyle="--", label=f"Umbral de aceptación ({_fmt(UMBRAL_ACEPTACION)})")
    eje.axhline(media, color="#2e8b57", linestyle=":", label=f"Promedio ({media:.1f})")
    eje.bar_label(barras, fmt="%.1f", fontsize=8)
    eje.set(ylim=(0, 105), ylabel="Puntaje SUS (0-100)", title="Puntaje SUS por participante")
    eje.legend(loc="lower right")
    figura.tight_layout()
    ruta = carpeta / "sus_por_participante.png"
    figura.savefig(ruta, dpi=200)
    plt.close(figura)
    creados.append(ruta)

    figura, eje = plt.subplots(figsize=(8, 4.5))
    medias = [statistics.fmean(p.contribuciones[i] for p in participantes) for i in range(10)]
    eje.barh([f"P{i + 1}" for i in range(10)][::-1], medias[::-1], color="#2f6fa3")
    eje.set(xlim=(0, 4), xlabel="Contribución media (0 = peor, 4 = mejor)", title="Contribución media por ítem")
    figura.tight_layout()
    ruta = carpeta / "sus_por_item.png"
    figura.savefig(ruta, dpi=200)
    plt.close(figura)
    creados.append(ruta)
    return creados


def main(argumentos: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Calcula el puntaje SUS a partir del CSV de Google Forms.")
    analizador.add_argument("csv", type=Path, help="CSV exportado de Google Forms")
    analizador.add_argument("--salida", type=Path, default=Path("resultados_sus"), help="carpeta de salida")
    opciones = analizador.parse_args(argumentos)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa otra codificación y deformaría las tildes
    try:
        participantes = leer_csv(opciones.csv)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    opciones.salida.mkdir(parents=True, exist_ok=True)
    texto = informe(participantes)
    (opciones.salida / "resultados_sus.md").write_text(texto, encoding="utf-8")
    imagenes = graficos(participantes, opciones.salida)
    print(texto)
    print(f"Informe: {opciones.salida / 'resultados_sus.md'}")
    print("Gráficos: " + (", ".join(str(i) for i in imagenes) if imagenes else "no se generaron (falta matplotlib: pip install matplotlib)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
