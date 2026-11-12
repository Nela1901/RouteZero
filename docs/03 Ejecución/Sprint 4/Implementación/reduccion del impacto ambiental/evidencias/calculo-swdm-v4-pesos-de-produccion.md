# Cálculo SWDM v4 con los pesos medidos en producción (salida del script)

Generado el 2026-11-10 con `python scripts/calcular_huella_swdm.py --antes-movil-kb 218 --antes-escritorio-kb 248 --despues-movil-kb 142 --despues-escritorio-kb 173` (pesos de Lighthouse en producción, ANTES del 2026-11-09 y DESPUÉS del 2026-11-10; mismo escenario de 10 400 visitas al año y 75 % desde celular). Método y verificación contra CO2.js en el [informe 01](../01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_6_0.md), sección 7.

[← Volver al README Principal](../../../../../../README.md)

---

## 1. Energía y emisión de una carga inicial (visita nueva, intensidad global 494 gCO2e/kWh)

| Perfil | Momento | Peso (KB) | Energía operativa (kWh) | Energía incorporada (kWh) | Energía total (kWh) | Emisión (g CO2e) |
|---|---|---|---|---|---|---|
| Móvil | ANTES | 218 | 4.331e-05 | 2.366e-05 | 6.697e-05 | 0.033083 |
| Móvil | DESPUÉS | 142 | 2.821e-05 | 1.541e-05 | 4.362e-05 | 0.021549 |
| Escritorio | ANTES | 248 | 4.927e-05 | 2.692e-05 | 7.619e-05 | 0.037636 |
| Escritorio | DESPUÉS | 173 | 3.437e-05 | 1.878e-05 | 5.315e-05 | 0.026254 |

## 2. Visita promedio (75% móvil) y proyección anual (10,400 visitas/año)

| Concepto | ANTES | DESPUÉS | Ahorro |
|---|---|---|---|
| Peso ponderado por visita (KB) | 225.50 | 149.75 | 33.6% |
| Emisión por visita (g CO2e) | 0.025837 | 0.017158 | 33.6% |
| Energía por visita (kWh) | 5.230e-05 | 3.473e-05 | 33.6% |
| Energía al año (kWh) | 0.5439 | 0.3612 | 0.1827 |
| Emisión al año (g CO2e) | 268.70 | 178.44 | 90.26 |

## 3. Sensibilidad del ahorro anual (g CO2e) a la intensidad de la red y al número de visitas

| Intensidad de la red | Visitas/año | ANTES | DESPUÉS | Ahorro |
|---|---|---|---|---|
| Global SWDM v4 (494 g/kWh) | 10,400 | 268.70 | 178.44 | 90.26 |
| Global SWDM v4 (494 g/kWh) | 104,000 | 2687.05 | 1784.41 | 902.63 |
| Global SWDM v4 (494 g/kWh) | 500,000 | 12918.49 | 8578.91 | 4339.58 |
| Diapositivas del curso (481 g/kWh) | 10,400 | 264.13 | 175.40 | 88.73 |
| Diapositivas del curso (481 g/kWh) | 104,000 | 2641.32 | 1754.05 | 887.27 |
| Diapositivas del curso (481 g/kWh) | 500,000 | 12698.65 | 8432.91 | 4265.73 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 10,400 | 235.24 | 156.22 | 79.02 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 104,000 | 2352.37 | 1562.16 | 790.21 |
| Perú en el dispositivo (263.27 g/kWh), resto global | 500,000 | 11309.48 | 7510.40 | 3799.08 |

---

[← Volver al README Principal](../../../../../../README.md)
