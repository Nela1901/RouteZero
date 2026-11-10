"""Huella de carbono de la transferencia de datos de RouteZero con el modelo SWDM v4 (Sustainable Web Design Model).

Solo usa la biblioteca estándar. Sirve para reproducir las tablas del informe de reducción del impacto ambiental:

    python scripts/calcular_huella_swdm.py
    python scripts/calcular_huella_swdm.py --visitas-anio 20000
    python scripts/calcular_huella_swdm.py --verificar

El modelo (Green Web Foundation, misma implementación que CO2.js 0.16.9) separa la energía de cada GB transferido en tres
segmentos y en dos componentes:

    energía operativa   (kWh/GB): centro de datos 0.055 + red 0.059 + dispositivo del usuario 0.080 = 0.194
    energía incorporada (kWh/GB): centro de datos 0.012 + red 0.013 + dispositivo del usuario 0.081 = 0.106 (fabricación del hardware)

    energía (kWh)  = GB transferidos x kWh/GB de cada segmento y componente
    emisión (gCO2e) = energía (kWh) x intensidad de la red eléctrica (gCO2e/kWh)

El descuento por hosting verde solo afecta a la energía operativa del centro de datos; Vercel y Render no figuran como
hosting verde en la Green Web Foundation (consulta del 10-11-2026), así que aquí vale 0.
"""

import argparse
import sys

# --- Constantes de SWDM v4 (iguales a CO2.js 0.16.9, constants/index.js) ---------------------------------------------
SEGMENTOS = ("centro de datos", "red", "dispositivo")
KWH_POR_GB_OPERATIVA = {"centro de datos": 0.055, "red": 0.059, "dispositivo": 0.080}
KWH_POR_GB_INCORPORADA = {"centro de datos": 0.012, "red": 0.013, "dispositivo": 0.081}
INTENSIDAD_GLOBAL = 494.0  # gCO2e/kWh: constante de SWDM v4 en CO2.js (las diapositivas del curso citan 481)
INTENSIDAD_DIAPOSITIVAS = 481.0
INTENSIDAD_PERU = 263.27  # gCO2e/kWh: promedio de Perú en los datos de CO2.js (average-intensities)
BYTES_POR_GB = 1_000_000_000  # CO2.js usa GB decimales
VISITA_NUEVA = 0.75  # SWDM: proporción de visitas con la caché vacía
VISITA_RETORNO = 0.25  # SWDM: proporción de visitas de retorno
CARGA_EN_RETORNO = 0.02  # SWDM: fracción de los datos que se vuelve a descargar en una visita de retorno
HOSTING_VERDE = 0.0  # factor de hosting verde (0 = no verde)


def energia_kwh(bytes_: float) -> dict[str, float]:
    """Energía en kWh de transferir `bytes_`, por componente y segmento."""
    gb = bytes_ / BYTES_POR_GB
    return {
        "operativa": gb * sum(KWH_POR_GB_OPERATIVA.values()),
        "incorporada": gb * sum(KWH_POR_GB_INCORPORADA.values()),
    }


def emision_g(bytes_: float, intensidad: float = INTENSIDAD_GLOBAL, intensidad_dispositivo: float | None = None) -> float:
    """gCO2e de una carga completa (visita nueva) de `bytes_`. `intensidad_dispositivo` permite usar la red del país del usuario."""
    gb = bytes_ / BYTES_POR_GB
    disp = intensidad if intensidad_dispositivo is None else intensidad_dispositivo
    total = 0.0
    for seg in SEGMENTOS:
        i = disp if seg == "dispositivo" else intensidad
        operativa = gb * KWH_POR_GB_OPERATIVA[seg] * i
        if seg == "centro de datos":
            operativa *= 1 - HOSTING_VERDE
        # Como en CO2.js, la intensidad elegida solo afecta a la energía operativa; la incorporada usa siempre la global
        total += operativa + gb * KWH_POR_GB_INCORPORADA[seg] * INTENSIDAD_GLOBAL
    return total


def emision_por_visita_g(bytes_: float, intensidad: float = INTENSIDAD_GLOBAL, intensidad_dispositivo: float | None = None) -> float:
    """gCO2e promedio por visita: 75 % de visitas nuevas y 25 % de retorno que recargan el 2 % de los datos."""
    nueva = emision_g(bytes_, intensidad, intensidad_dispositivo)
    return nueva * VISITA_NUEVA + nueva * CARGA_EN_RETORNO * VISITA_RETORNO


def verificar() -> int:
    """Contrasta el cálculo con los valores que devuelve `new co2({ model: 'swd', version: 4 }).perByte(bytes)` de CO2.js 0.16.9."""
    ok = True

    def comparar(titulo: str, calculado: float, referencia: float) -> None:
        nonlocal ok
        bien = abs(calculado - referencia) < 5e-7
        ok &= bien
        print(f"{titulo}: calculado {calculado:.6f} g, CO2.js {referencia:.6f} g -> {'coincide' if bien else 'NO COINCIDE'}")

    # perByte(bytes): una carga completa, intensidad global
    for kb, ref in {140: 0.021246, 171: 0.025950, 213: 0.032324, 244: 0.037029}.items():
        comparar(f"Carga de {kb} KB", emision_g(kb * 1024), ref)
    # perVisitTrace(bytes, false, {75 % visitas nuevas, 25 % de retorno, 2 % recargado}): la visita promedio del informe
    comparar("Visita ANTES (220.75 KB)", emision_por_visita_g(220.75 * 1024), 0.025293)
    comparar("Visita DESPUÉS (147.75 KB)", emision_por_visita_g(147.75 * 1024), 0.016929)
    # gridIntensity: { device: { country: "PER" } }
    comparar("Visita ANTES, dispositivo en Perú", emision_por_visita_g(220.75 * 1024, INTENSIDAD_GLOBAL, INTENSIDAD_PERU), 0.022143)
    comparar("Visita DESPUÉS, dispositivo en Perú", emision_por_visita_g(147.75 * 1024, INTENSIDAD_GLOBAL, INTENSIDAD_PERU), 0.014820)
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # las tablas llevan tildes; así salen bien también al redirigir a un archivo
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes-movil-kb", type=float, default=213, help="peso de la carga inicial antes de optimizar, en móvil (KB)")
    ap.add_argument("--antes-escritorio-kb", type=float, default=244)
    ap.add_argument("--despues-movil-kb", type=float, default=140)
    ap.add_argument("--despues-escritorio-kb", type=float, default=171)
    ap.add_argument("--proporcion-movil", type=float, default=0.75, help="parte de las visitas desde el celular (los 15 conductores de 20 usuarios)")
    ap.add_argument("--visitas-anio", type=int, default=10_400, help="visitas al año: 20 usuarios x 260 días hábiles x 2 sesiones")
    ap.add_argument("--verificar", action="store_true", help="contrasta el cálculo con CO2.js y termina")
    a = ap.parse_args()
    if a.verificar:
        return verificar()

    kb = 1024
    print("## 1. Energía y emisión de una carga inicial (visita nueva, intensidad global 494 gCO2e/kWh)\n")
    print("| Perfil | Momento | Peso (KB) | Energía operativa (kWh) | Energía incorporada (kWh) | Energía total (kWh) | Emisión (g CO2e) |")
    print("|---|---|---|---|---|---|---|")
    casos = [
        ("Móvil", "ANTES", a.antes_movil_kb), ("Móvil", "DESPUÉS", a.despues_movil_kb),
        ("Escritorio", "ANTES", a.antes_escritorio_kb), ("Escritorio", "DESPUÉS", a.despues_escritorio_kb),
    ]
    for perfil, momento, peso in casos:
        e = energia_kwh(peso * kb)
        print(f"| {perfil} | {momento} | {peso:.0f} | {e['operativa']:.3e} | {e['incorporada']:.3e} | {e['operativa'] + e['incorporada']:.3e} | {emision_g(peso * kb):.6f} |")

    mov = a.proporcion_movil
    antes = (mov * a.antes_movil_kb + (1 - mov) * a.antes_escritorio_kb) * kb
    despues = (mov * a.despues_movil_kb + (1 - mov) * a.despues_escritorio_kb) * kb
    print(f"\n## 2. Visita promedio ({mov:.0%} móvil) y proyección anual ({a.visitas_anio:,} visitas/año)\n")
    print("| Concepto | ANTES | DESPUÉS | Ahorro |")
    print("|---|---|---|---|")
    print(f"| Peso ponderado por visita (KB) | {antes / kb:.2f} | {despues / kb:.2f} | {(1 - despues / antes):.1%} |")
    v_a, v_d = emision_por_visita_g(antes), emision_por_visita_g(despues)
    print(f"| Emisión por visita (g CO2e) | {v_a:.6f} | {v_d:.6f} | {(1 - v_d / v_a):.1%} |")
    en_a = (energia_kwh(antes)["operativa"] + energia_kwh(antes)["incorporada"]) * (VISITA_NUEVA + CARGA_EN_RETORNO * VISITA_RETORNO)
    en_d = (energia_kwh(despues)["operativa"] + energia_kwh(despues)["incorporada"]) * (VISITA_NUEVA + CARGA_EN_RETORNO * VISITA_RETORNO)
    print(f"| Energía por visita (kWh) | {en_a:.3e} | {en_d:.3e} | {(1 - en_d / en_a):.1%} |")
    print(f"| Energía al año (kWh) | {en_a * a.visitas_anio:.4f} | {en_d * a.visitas_anio:.4f} | {(en_a - en_d) * a.visitas_anio:.4f} |")
    print(f"| Emisión al año (g CO2e) | {v_a * a.visitas_anio:.2f} | {v_d * a.visitas_anio:.2f} | {(v_a - v_d) * a.visitas_anio:.2f} |")

    print("\n## 3. Sensibilidad del ahorro anual (g CO2e) a la intensidad de la red y al número de visitas\n")
    print("| Intensidad de la red | Visitas/año | ANTES | DESPUÉS | Ahorro |")
    print("|---|---|---|---|---|")
    escenarios = [
        ("Global SWDM v4 (494 g/kWh)", INTENSIDAD_GLOBAL, None),
        ("Diapositivas del curso (481 g/kWh)", INTENSIDAD_DIAPOSITIVAS, None),
        ("Perú en el dispositivo (263.27 g/kWh), resto global", INTENSIDAD_GLOBAL, INTENSIDAD_PERU),
    ]
    for nombre, i, i_disp in escenarios:
        for visitas in (a.visitas_anio, a.visitas_anio * 10, 500_000):
            x, y = emision_por_visita_g(antes, i, i_disp) * visitas, emision_por_visita_g(despues, i, i_disp) * visitas
            print(f"| {nombre} | {visitas:,} | {x:.2f} | {y:.2f} | {x - y:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
