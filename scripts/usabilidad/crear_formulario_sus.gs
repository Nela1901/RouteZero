/**
 * Evaluación de usabilidad — RouteZero (escala SUS).
 *
 * Crea en la cuenta de Google de quien lo ejecuta un formulario de Google Forms con:
 *   1. Tres preguntas de contexto (rol con el que se probó el sistema, dispositivo y experiencia previa).
 *   2. Los 10 ítems de la System Usability Scale (SUS), en el orden original y en escala de 1 a 5.
 *   3. Dos preguntas abiertas opcionales para identificar los puntos de la interfaz que costaron más.
 *
 * Cómo usarlo:
 *   1. Abrir https://script.google.com y crear un proyecto nuevo (nombrarlo «RouteZero»).
 *   2. Pegar este archivo completo, guardar, elegir la función `crearFormularioSUS` y pulsar «Ejecutar».
 *   3. Aceptar los permisos que pide Google (solo crea y edita formularios de esa cuenta).
 *   4. Abrir «Registro de ejecución» (Ver > Registros): ahí aparecen la URL para responder y la URL de edición.
 *
 * Ejecutar la función otra vez crea OTRO formulario: no la repitas si ya tienes el correcto.
 *
 * Fuente de la escala: Brooke, J. (1996). SUS: A quick and dirty usability scale. En P. W. Jordan et al. (Eds.),
 * Usability evaluation in industry (pp. 189-194). Taylor & Francis. Los enunciados están en español y se conservan
 * en el orden original porque el cálculo del puntaje depende de la posición de cada ítem (impares positivos y pares
 * negativos). No cambies el orden ni el sentido de los enunciados.
 */

const APLICACION = "RouteZero";

// Los 10 ítems de la SUS (traducción al español del material del curso). El número es la posición original.
const ITEMS_SUS = [
  "Creo que me gustaría usar este sistema con regularidad.",
  "Encuentro que este sistema es innecesariamente complejo.",
  "Considero que el sistema es fácil de usar.",
  "Creo que necesitaría ayuda de una persona con experiencia para usar este sistema.",
  "Creo que las diversas funciones de este sistema están bien integradas.",
  "Creo que hay demasiada inconsistencia en este sistema.",
  "Imagino que la mayoría de las personas aprenderían a usar este sistema muy rápidamente.",
  "Encuentro que el sistema es muy complicado de usar.",
  "Me siento confiado usando este sistema.",
  "Necesitaría aprender muchas cosas antes de poder usar este sistema.",
];

// Preguntas de contexto: describen la muestra (perfil) sin identificar a nadie.
const CONTEXTO = [
  {
    titulo: "¿Con qué rol probaste el sistema?",
    opciones: ["Administrador", "Operador", "Conductor"],
  },
  {
    titulo: "¿En qué dispositivo lo usaste?",
    opciones: ["Computadora", "Celular"],
  },
  {
    titulo: "¿Qué experiencia tenías antes con sistemas de gestión de pedidos, rutas o reparto?",
    opciones: ["Ninguna", "Poca", "Media", "Mucha"],
  },
];

const DESCRIPCION =
  "Esta encuesta evalúa qué tan fácil de usar es " + APLICACION + ", un sistema web de optimización de rutas de " +
  "reparto. Forma parte de un trabajo académico de la Universidad Continental (Taller de Proyectos 2).\n\n" +
  "ANTES DE RESPONDER: usa el sistema realizando las tareas que te indicó la persona que dirige la prueba. " +
  "Responde apenas termines, con tu primera impresión; no hace falta pensar demasiado cada afirmación.\n\n" +
  "CÓMO RESPONDER: valora cada afirmación según tu experiencia directa con el sistema, de 1 a 5:\n" +
  "1 = Totalmente en desacuerdo · 2 = En desacuerdo · 3 = Ni de acuerdo ni en desacuerdo · " +
  "4 = De acuerdo · 5 = Totalmente de acuerdo.\n" +
  "Si una afirmación no puedes responderla, marca 3. Todas las respuestas son obligatorias salvo las dos últimas " +
  "preguntas abiertas.\n\n" +
  "No hay respuestas correctas o incorrectas: responde con sinceridad y de forma independiente.\n\n" +
  "PRIVACIDAD: este formulario no pide nombre ni correo y no exige iniciar sesión con una cuenta de Google. " +
  "Las respuestas solo se usan, de forma agrupada, en el informe del trabajo.";

/** Ejecuta un ajuste del formulario; si Google no lo permite en esta cuenta, lo anota en el registro y continúa. */
function aplicar(descripcion, ajuste) {
  try {
    ajuste();
  } catch (error) {
    Logger.log("AVISO: no se pudo aplicar «" + descripcion + "» (" + error.message + "). Revísalo a mano en Configuración.");
  }
}

function crearFormularioSUS() {
  if (ITEMS_SUS.length !== 10) {
    throw new Error("La SUS requiere exactamente 10 ítems; hay " + ITEMS_SUS.length + ".");
  }

  const form = FormApp.create("Evaluación de usabilidad — " + APLICACION + " (SUS)");
  form.setDescription(DESCRIPCION);

  // Privacidad: sin correos y sin límite por cuenta (que obligaría a identificarse). No se usa `setRequireLogin`:
  // solo existe en cuentas de Google Workspace, y en una cuenta personal el formulario ya no exige iniciar sesión.
  // Cada ajuste se aplica por separado: si alguno no está disponible en tu cuenta, avisa en el registro y sigue.
  aplicar("no recopilar correos", function () { form.setCollectEmail(false); });
  aplicar("sin límite de una respuesta por cuenta", function () { form.setLimitOneResponsePerUser(false); });
  aplicar("sin edición de respuestas", function () { form.setAllowResponseEdits(false); });
  aplicar("sin enlace para responder de nuevo", function () { form.setShowLinkToRespondAgain(false); });
  aplicar("barra de progreso", function () { form.setProgressBar(true); });
  aplicar("mensaje de confirmación", function () {
    form.setConfirmationMessage("¡Gracias! Tu respuesta quedó registrada.");
  });

  // Sección 1: contexto de la prueba.
  CONTEXTO.forEach(function (pregunta) {
    form
      .addMultipleChoiceItem()
      .setTitle(pregunta.titulo)
      .setChoiceValues(pregunta.opciones)
      .setRequired(true);
  });

  // Sección 2: escala SUS. Cada título empieza por «P1.», «P2.»... : el script de procesamiento reconoce así las columnas.
  form.addPageBreakItem().setTitle("Escala de usabilidad (SUS)").setHelpText(
    "Valora cada afirmación de 1 (Totalmente en desacuerdo) a 5 (Totalmente de acuerdo)."
  );
  ITEMS_SUS.forEach(function (texto, i) {
    form
      .addScaleItem()
      .setTitle("P" + (i + 1) + ". " + texto)
      .setBounds(1, 5)
      .setLabels("Totalmente en desacuerdo", "Totalmente de acuerdo")
      .setRequired(true);
  });

  // Sección 3: comentarios opcionales (no entran en el puntaje; sirven para ubicar los cuellos de botella).
  form.addPageBreakItem().setTitle("Comentarios (opcionales)");
  form
    .addParagraphTextItem()
    .setTitle("¿Qué fue lo que más te costó o te confundió al usar el sistema?")
    .setRequired(false);
  form
    .addParagraphTextItem()
    .setTitle("¿Qué cambiarías o mejorarías?")
    .setRequired(false);

  Logger.log("Formulario creado: Evaluación de usabilidad — " + APLICACION + " (SUS)");
  Logger.log("URL para responder (compártela con los participantes): " + form.getPublishedUrl());
  Logger.log("URL de edición (solo para ti): " + form.getEditUrl());
}
