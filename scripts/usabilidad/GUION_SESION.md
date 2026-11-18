# Guion de la sesión de prueba de usabilidad (SUS)

Sesión individual de unos 15 minutos con una persona, sobre el sistema desplegado. **Quien dirige la sesión** (moderador) inicia sesión con la cuenta de prueba del rol y le entrega el dispositivo; el participante hace las tareas **sin ayuda**. Las contraseñas no se escriben en este guion ni en ningún documento.

## 1. Antes de la sesión (moderador)

1. Despertar el servidor: abrir `https://routezero-7k7j.onrender.com/api/health` y esperar la respuesta (Render gratuito tarda hasta un minuto la primera vez).
2. Abrir el sistema en `https://route-zero-omega.vercel.app` con el navegador y el dispositivo que usará el participante: **computadora** para Administrador y Operador, **celular** para Conductor.
3. Iniciar sesión con la cuenta del rol que probará (el participante no necesita la contraseña).
4. Solo para el rol Conductor: dejar lista la ruta de demostración de hoy (`python backend/tests_manual/demo_conductor.py crear`; si quedó una de la sesión anterior, ejecutar antes `limpiar`). La entrega se registra de verdad, por eso se recrea la ruta entre un participante y el siguiente.
5. Tener a mano la hoja de observación (sección 4) y un cronómetro.

## 2. Qué se le dice al participante

> «Vamos a probar un sistema web de rutas de reparto. Lo que se evalúa es el sistema, **no a ti**: si algo te cuesta, es un problema del sistema y me ayuda saberlo. Haré unas tareas simples, en voz alta si te sirve, y no te voy a ayudar mientras las haces. Al terminar responderás una encuesta corta. No se anota tu nombre ni tu correo.»

Si el participante pregunta cómo se hace algo, responder «haz lo que te parezca natural» y anotar la duda. Solo se interviene si lleva más de 3 minutos atascado en una tarea (se marca «con ayuda» o «no completó»).

## 3. Tareas por rol

Criterio de éxito entre paréntesis. Se lee una tarea a la vez.

### Administrador (computadora)

| # | Tarea | Éxito |
|---|---|---|
| A1 | «Ve a la sección de Sostenibilidad.» | Llega a la pantalla «Sostenibilidad» desde el menú. |
| A2 | «Elige el mes anterior y descarga el reporte en PDF.» | El PDF se descarga, o entiende y explica el aviso de que no hay datos en ese periodo. |
| A3 | «Ve a Rutas, genera las rutas del día y, cuando aparezcan, descarta el borrador.» | Pulsa «Generar rutas», espera el cálculo (puede tardar hasta 30 s) y descarta con «Descartar». |

### Operador (computadora)

| # | Tarea | Éxito |
|---|---|---|
| O1 | «Registra un pedido nuevo para un cliente de la lista: descripción “Prueba de usabilidad”, peso 5 kg, prioridad estándar.» | El pedido aparece registrado. |
| O2 | «Encuentra ese pedido en la lista.» | Localiza el pedido con la descripción indicada. |
| O3 | «Cancela ese pedido.» | Pulsa «Cancelar pedido» y confirma; el pedido queda cancelado. |

### Conductor (celular)

| # | Tarea | Éxito |
|---|---|---|
| C1 | «Dime cuál es tu siguiente parada y a qué cliente le toca.» | Identifica la parada y el cliente de la tarjeta «Siguiente parada». |
| C2 | «Registra que ya entregaste ese pedido.» | Pulsa «Entregado» y confirma con «Sí, entregado». |
| C3 | «¿Cuántas entregas llevas hechas?» | Lee el contador de entregas (por ejemplo, «1 de 6 entregas»). |

## 4. Hoja de observación (una por participante)

Código del participante: **P__** (se asigna por orden de llegada: P01, P02…; no se anota nombre).

| Tarea | ¿Completó? (sí / con ayuda / no) | Tiempo (s) | Errores o dudas observadas |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

Rol: ____  Dispositivo: ____  Hora: ____

Al final se calcula por tarea: **tasa de éxito** (sí / total de participantes) y **tiempo mediano**. Las tareas con más ayudas o más tiempo son los cuellos de botella que se reportan en el informe.

## 5. Después de las tareas

1. **Sin comentar nada del sistema todavía**, entregar el enlace de la encuesta SUS y pedir que responda enseguida, con la primera impresión.
2. Cuando termine, conversar dos minutos: «¿qué fue lo que más te costó?» y «¿qué cambiarías?». Anotar las respuestas en la hoja.
3. Cerrar la sesión en el sistema (botón «Cerrar sesión») y, si fue Conductor, recrear la ruta de demostración para el siguiente participante.

## 6. Al terminar el día

- Ejecutar `python backend/tests_manual/demo_conductor.py limpiar` si quedó la ruta de demostración.
- Los pedidos de prueba cancelados quedan en el historial con la descripción «Prueba de usabilidad»: es esperado y no afecta a los datos de la demostración.
- Descargar las respuestas de la encuesta (Respuestas → ⋮ → Descargar respuestas .csv) y procesarlas con `python scripts/usabilidad/procesar_sus.py respuestas.csv`. **El CSV no se sube al repositorio.**
