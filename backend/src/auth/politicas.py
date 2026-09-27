"""Parámetros de negocio de las sesiones, compartidos por el servicio y los jobs de mantenimiento."""

# Un refresh token ya rotado se acepta todavía este tiempo: cubre dos pestañas que renuevan a
# la vez o un reintento por red lenta. Pasado ese tiempo, usarlo se considera robo de sesión.
VENTANA_GRACIA_SEGUNDOS = 10

# Una sesión que no se renueva en este tiempo caduca (el plan gratuito de Supabase no permite
# configurar un tope de sesión, así que lo hacemos cumplir nosotros).
DIAS_VIGENCIA_REFRESH = 7

# Las sesiones cerradas (REVOCADA/EXPIRADA) se conservan este tiempo y luego se borran, para que
# la tabla no crezca indefinidamente.
DIAS_RETENCION_CERRADAS = 30
