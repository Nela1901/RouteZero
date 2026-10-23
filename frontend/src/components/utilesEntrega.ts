/** Textos y marcas de las paradas de una ruta, compartidos por el mapa y la vista del conductor. */

const MARCAS: Record<string, string> = { ENTREGADO: "✓", FALLIDO: "✗" };
const TEXTOS_DE_ENTREGA: Record<string, string> = { PENDIENTE: "Pendiente de entrega", ENTREGADO: "Entregado" };

/** Símbolo que se dibuja sobre la parada: ✕ si el pedido se canceló, ✓ entregado, ✗ fallido y nada si está pendiente. */
export function marcaDeEntrega(cancelada: boolean, estado: string): string {
  return cancelada ? "✕" : (MARCAS[estado] ?? "");
}

export function textoDeEntrega(cancelada: boolean, estado: string): string {
  return cancelada ? "Pedido cancelado" : (TEXTOS_DE_ENTREGA[estado] ?? "Entrega fallida");
}

export const ETIQUETA_ESTADO_RUTA: Record<string, string> = { EN_EJECUCION: "En ejecución", COMPLETADA: "Completada" };
