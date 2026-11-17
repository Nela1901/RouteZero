# Costo de usar `moment` y `lodash` frente a las APIs nativas (medición)

Medido el 2026-11-12 en una carpeta temporal, sin tocar el proyecto. Sirve como «costo evitado» del área 5 del [informe 01](../01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_6_0.md): RouteZero no usa esas librerías, así que no existe un ANTES; esta medición muestra cuánto habría costado usarlas.

[← Volver al README Principal](../../../../README.md)

---

## Método

Se empaquetó con `esbuild --bundle --minify` el mismo ejemplo mínimo, escrito de dos maneras, y se midió su tamaño sin comprimir y comprimido con `gzip -9`.

**Con librerías** (`moment@2.30.1` y `lodash@4.17.21`, importadas completas):

```js
import moment from "moment";
import { uniq, groupBy } from "lodash";
console.log(moment("2026-11-13").format("DD/MM/YYYY"), uniq([1, 1, 2]), groupBy([1, 2, 3], (n) => n % 2));
```

**Con APIs nativas** (lo que hace RouteZero):

```js
console.log(new Date("2026-11-13T00:00:00").toLocaleDateString("es-PE"), [...new Set([1, 1, 2])], Object.groupBy([1, 2, 3], (n) => n % 2));
```

## Resultado

| Versión | Sin comprimir | Comprimido (gzip) |
|---|---|---|
| `moment` + `lodash` | 135 629 B (135.6 KB) | 46 413 B (46.4 KB) |
| APIs nativas | 223 B | 215 B |

El JavaScript inicial de RouteZero pesa 87.4 KB comprimidos; las dos librerías habrían sumado 46.4 KB, es decir, **un 53 % más**.

## Alcance y límites

- Es un ejemplo mínimo con las librerías completas. `lodash` en su versión estándar no se puede recortar bien; con `lodash-es` o `moment` sin idiomas el costo sería menor. El orden de magnitud no cambia.
- No es un cambio hecho en RouteZero: es lo que se evita al usar las APIs nativas desde el diseño.

---

[← Volver al README Principal](../../../../README.md)
