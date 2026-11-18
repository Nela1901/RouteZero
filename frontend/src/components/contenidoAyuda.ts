/**
 * Contenido de la guía de primeros pasos y de las preguntas frecuentes. Cada afirmación describe lo que la interfaz hace de verdad
 * (nombres de botones, secciones y reglas por rol). Los fragmentos entre **dobles asteriscos** se muestran en negrita.
 *
 * Nace de la evaluación de usabilidad con la escala SUS (documento «04 Usabilidad»): los ítems sobre necesitar ayuda y aprender antes
 * de usar el sistema fueron los más bajos, y 8 de 10 comentarios pedían una explicación inicial.
 */

export type RolAyuda = "ADMINISTRADOR" | "OPERADOR" | "CONDUCTOR";

export const ETIQUETA_ROL: Record<RolAyuda, string> = {
  ADMINISTRADOR: "administrador",
  OPERADOR: "operador",
  CONDUCTOR: "conductor",
};

export interface Guia {
  introduccion: string;
  pasos: string[];
}

export const GUIAS: Record<RolAyuda, Guia> = {
  ADMINISTRADOR: {
    introduccion: "El administrador prepara los datos, genera y confirma las rutas y sigue la operación. Este es el orden habitual:",
    pasos: [
      "Entra a **Mapa**, la pantalla de inicio. Muestra las rutas del día en vivo, sus paradas numeradas y la congestión de las vías principales.",
      "En **Flota**, **Conductores** y **Clientes** registra lo que el sistema necesita: los vehículos con su capacidad, los conductores con su licencia y su horario, y los clientes con su ubicación y su horario de atención.",
      "En **Pedidos** pulsa **Registrar pedido** y completa el cliente, la descripción, el peso y la prioridad (express, estándar o económico). Los pedidos pendientes son los que el sistema reparte en rutas.",
      "En **Rutas** elige la fecha y pulsa **Generar rutas**. El cálculo puede tardar hasta medio minuto y deja un **borrador**, que en el mapa se dibuja con línea discontinua.",
      "Revisa el borrador. **Confirmar rutas** hace que los conductores las vean; **Descartar** lo elimina y los pedidos siguen pendientes.",
      "Con las rutas en curso, sigue las entregas en el **Mapa**. Si hay un incidente de tráfico, regístralo en el panel de incidentes de **Rutas** y pulsa **Re-optimizar rutas**.",
      "En **Sostenibilidad** consulta el CO₂ emitido, el combustible ahorrado y el plan de compensación, y descarga el informe con **Descargar reporte PDF**.",
      "En **Seguridad** activa la verificación en dos pasos y revisa las sesiones abiertas de tu cuenta.",
    ],
  },
  OPERADOR: {
    introduccion: "El operador registra los pedidos y consulta las rutas. Este es el orden habitual:",
    pasos: [
      "Entra a **Mapa**, la pantalla de inicio, para ver las rutas del día y sus paradas.",
      "En **Clientes** consulta y registra los negocios a los que se reparte, con su ubicación y su horario de atención.",
      "En **Pedidos** pulsa **Registrar pedido** y completa el cliente, la descripción, el peso y la prioridad (express, estándar o económico). Mientras un pedido no se haya entregado puedes cancelarlo con **Cancelar pedido**.",
      "En **Rutas** consulta las rutas y su estado. Generarlas, confirmarlas y re-optimizarlas lo hace el administrador.",
      "En **Seguridad** activa la verificación en dos pasos y revisa las sesiones abiertas de tu cuenta.",
    ],
  },
  CONDUCTOR: {
    introduccion: "El conductor ve su ruta del día y registra cada entrega desde el celular. Este es el orden habitual:",
    pasos: [
      "Tu ruta aparece cuando el administrador la confirma. Si ves **Sin ruta por ahora**, todavía no tienes una asignada. Si ves **Cuenta sin vincular**, pide al administrador que registre tu correo en tu ficha de conductor.",
      "Arriba ves tu avance (por ejemplo, «1 de 6 entregas») y debajo la tarjeta **Siguiente parada**, con el cliente, la hora estimada y la prioridad.",
      "El mapa muestra tu recorrido y las paradas numeradas. Si una calle de tu ruta tiene congestión, aparece una alerta con la marca **En tu ruta**.",
      "Cuando entregues el pedido pulsa **Entregado** y confirma. Si no pudiste entregarlo, pulsa **No se pudo** y confirma. Después pasas a la siguiente parada.",
      "Las paradas ya atendidas quedan en la lista **Paradas atendidas**. La pantalla se actualiza sola cada 30 segundos; también puedes pulsar **Actualizar**.",
    ],
  },
};

export interface ElementoMapa {
  etiqueta: string;
  detalle: string;
}

/** Cómo leer el mapa (lo que muestran su leyenda y su panel de congestión). Solo para quienes usan el panel de operaciones. */
export const LEYENDA_MAPA: ElementoMapa[] = [
  { etiqueta: "Parada entregada ✓", detalle: "se dibuja en verde." },
  { etiqueta: "Parada fallida ✗", detalle: "en rojo: no se pudo entregar. El pedido sigue asignado para reprogramarlo." },
  { etiqueta: "Parada cancelada ✕", detalle: "en gris: el pedido se canceló." },
  { etiqueta: "Parada pendiente", detalle: "con el color de su ruta, numerada en el orden de entrega." },
  { etiqueta: "Línea discontinua", detalle: "es un borrador que todavía no se confirmó." },
  { etiqueta: "Congestión", detalle: "las vías con tráfico moderado o alto se marcan en amarillo o rojo; es más probable en hora punta (7:30 a 9:30, 12:00 a 14:30 y 17:00 a 21:00)." },
  { etiqueta: "Controles", detalle: "puedes ocultar una ruta para ver las demás y cambiar la hora para ver cómo estaría la congestión a esa hora." },
];

export const TEXTO_VERIFICACION = [
  "Es una capa extra de seguridad: además de tu contraseña, el sistema te pide un **código de 6 dígitos**. Ese código lo genera una aplicación de autenticación en tu teléfono, como Google Authenticator o Authy, y cambia cada 30 segundos.",
  "Si tu cuenta la tiene activada, el código se pide **después de escribir la contraseña**. Para activarla entra a **Seguridad**, pulsa **Activar verificación en dos pasos**, escanea el código QR con la aplicación y escribe el código que te muestre.",
];

export interface Pregunta {
  pregunta: string;
  respuesta: string;
  roles: RolAyuda[];
}

const TODOS: RolAyuda[] = ["ADMINISTRADOR", "OPERADOR", "CONDUCTOR"];
const PANEL: RolAyuda[] = ["ADMINISTRADOR", "OPERADOR"];

export const PREGUNTAS: Pregunta[] = [
  {
    pregunta: "¿Por qué lo primero que veo es el mapa y no un resumen?",
    respuesta:
      "El mapa es la pantalla que más se usa durante el día. El resumen de indicadores (distancia, CO₂, combustible ahorrado, cumplimiento de ventanas y ahorro en soles) está en **Sostenibilidad**, que solo ven los administradores; el CO₂ emitido hoy también aparece arriba, junto al botón de tema.",
    roles: PANEL,
  },
  {
    pregunta: "¿Por qué la primera vez que entro tarda tanto?",
    respuesta:
      "El servicio gratuito en el que está alojado el sistema se apaga después de un rato sin uso. La primera carga puede tardar hasta un minuto; después responde rápido.",
    roles: TODOS,
  },
  {
    pregunta: "¿Cuánto tarda en generar las rutas?",
    respuesta:
      "Depende de cuántos pedidos y vehículos haya; con muchos pedidos puede tomar hasta medio minuto. Mientras calcula, el botón muestra un contador de segundos.",
    roles: ["ADMINISTRADOR"],
  },
  {
    pregunta: "¿Qué diferencia hay entre generar, confirmar y descartar?",
    respuesta:
      "**Generar rutas** calcula un borrador, que todavía no ven los conductores. **Confirmar rutas** lo vuelve real: los pedidos pasan a asignados y cada conductor ve su ruta. **Descartar** elimina el borrador y los pedidos siguen pendientes.",
    roles: ["ADMINISTRADOR"],
  },
  {
    pregunta: "¿Cómo registro un incidente de tráfico?",
    respuesta:
      "En **Rutas**, en el panel de incidentes. Se pueden registrar para Av. Ferrocarril, Av. Giráldez y Calle Real, con qué tanto más lento está el tránsito. Después pulsa **Re-optimizar rutas** para que el sistema reordene lo que falta de las rutas en curso; lo ya entregado no cambia.",
    roles: ["ADMINISTRADOR"],
  },
  {
    pregunta: "¿Qué pasa con una entrega que no se pudo realizar?",
    respuesta:
      "El conductor la marca con **No se pudo**. En el mapa la parada queda como fallida y el pedido sigue asignado, de modo que el administrador puede reprogramarlo al re-optimizar.",
    roles: TODOS,
  },
  {
    pregunta: "¿Puedo deshacer una entrega que ya registré?",
    respuesta: "No. Por eso el sistema te pide confirmar antes de registrar una entrega como **Entregado** o como **No se pudo**.",
    roles: ["CONDUCTOR"],
  },
  {
    pregunta: "¿Qué puede ver cada rol?",
    respuesta:
      "Los **administradores** ven todas las secciones. Los **operadores** ven Mapa, Clientes, Rutas, Pedidos y Seguridad; no ven Flota, Conductores ni Sostenibilidad. Los **conductores** solo ven su ruta del día.",
    roles: PANEL,
  },
  {
    pregunta: "¿La información se actualiza sola?",
    respuesta:
      "Sí. El mapa vuelve a pedir las rutas cada 30 segundos y la vista del conductor también se actualiza cada 30 segundos.",
    roles: TODOS,
  },
  {
    pregunta: "¿Puedo cambiar entre el tema claro y el oscuro?",
    respuesta: "Sí, con el botón de tema que está en la parte superior de la pantalla. Tu elección se recuerda en ese navegador.",
    roles: TODOS,
  },
  {
    pregunta: "¿Cómo cierro mi sesión?",
    respuesta: "Con el botón **Cerrar sesión**: en el menú lateral si usas el panel de operaciones, o en la barra de abajo si eres conductor.",
    roles: TODOS,
  },
];
