# Cálculo de la huella de carbono con SWDM v4 (salida del script)

Generado el 2026-11-09 con `python scripts/calcular_huella_swdm.py` (valores por defecto: 20 usuarios × 260 días × 2 sesiones = 10 400 visitas/año, 75 % desde celular). El script y su verificación contra CO2.js están descritos en el [informe 01](../01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_6_0.md), sección 7.

[← Volver al README Principal](../../../../README.md)

---

## 1. Energía y emisión de una carga inicial (visita nueva, intensidad global 494 gCO2e/kWh)

| Perfil | Momento | Peso (KB) | Energía operativa (kWh) | Energía incorporada (kWh) | Energía total (kWh) | Emisión (g CO2e) |
|---|---|---|---|---|---|---|
| Móvil | ANTES | 213 | 4.231e-05 | 2.312e-05 | 6.543e-05 | 0.032324 |
| Móvil | DESPUÉS | 140 | 2.781e-05 | 1.520e-05 | 4.301e-05 | 0.021246 |
| Escritorio | ANTES | 244 | 4.847e-05 | 2.648e-05 | 7.496e-05 | 0.037029 |
| Escritorio | DESPUÉS | 171 | 3.397e-05 | 1.856e-05 | 5.253e-05 | 0.025950 |

## 2. Visita promedio (75% móvil) y proyección anual (10,400 visitas/año)

| Concepto | ANTES | DESPUÉS | Ahorro |
|---|---|---|---|
| Peso ponderado por visita (KB) | 220.75 | 147.75 | 33.1% |
| Emisión por visita (g CO2e) | 0.025293 | 0.016929 | 33.1% |
| Energía por visita (kWh) | 5.120e-05 | 3.427e-05 | 33.1% |
| Energía al año (kWh) | 0.5325 | 0.3564 | 0.1761 |
| Emisión al año (g CO2e) | 263.04 | 176.06 | 86.99 |

## 3. Sensibilidad del ahorro anual (g CO2e) a la intensidad de la red y al número de visitas

| Intensidad de la red | Visitas/año | ANTES | DESPUÉS | Ahorro |
|---|---|---|---|---|
| Global SWDM v4 (494 g/kWh) | 10,400 | 263.04 | 176.06 | 86.99 |
| Global SWDM v4 (494 g/kWh) | 104,000 | 2630.44 | 1760.58 | 869.86 |
| Global SWDM v4 (494 g/kWh) | 500,000 | 12646.37 | 8464.33 | 4182.04 |
| Diapositivas del curso (481 g/kWh) | 10,400 | 258.57 | 173.06 | 85.51 |
| Diapositivas del curso (481 g/kWh) | 104,000 | 2585.68 | 1730.62 | 855.06 |
| Diapositivas del curso (481 g/kWh) | 500,000 | 12431.16 | 8320.29 | 4110.87 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 10,400 | 230.28 | 154.13 | 76.15 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 104,000 | 2302.82 | 1541.30 | 761.52 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 500,000 | 11071.26 | 7410.09 | 3661.16 |

---

[← Volver al README Principal](../../../../README.md)
