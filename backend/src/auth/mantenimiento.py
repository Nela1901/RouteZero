"""Jobs periódicos de mantenimiento de `sesiones_activas`.

Se ejecuta a mano o desde un cron (p. ej. un Cron Job de Render), desde `backend/`:

    python -m src.auth.mantenimiento

Usa `DATABASE_ADMIN_URL` (rol `app_admin`, con BYPASSRLS): la API web nunca se conecta con ese
rol, pero estos jobs necesitan ver las sesiones de todos los usuarios.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.auth.politicas import DIAS_RETENCION_CERRADAS, DIAS_VIGENCIA_REFRESH
from src.core.config import settings
from src.core.database import url_con_driver_explicito


def marcar_expiradas(session: Session) -> int:
    """Sesiones ACTIVAS sin renovar durante más de la vigencia del refresh token → EXPIRADA."""
    resultado = session.execute(
        text(
            "UPDATE sesiones_activas SET estado = 'EXPIRADA' "
            "WHERE estado = 'ACTIVA' "
            "AND ultimo_uso_en < CURRENT_TIMESTAMP - make_interval(days => :dias)"
        ),
        {"dias": DIAS_VIGENCIA_REFRESH},
    )
    return resultado.rowcount


def borrar_cerradas_antiguas(session: Session) -> int:
    """Borra las sesiones REVOCADA/EXPIRADA cuya última actividad supera la retención.

    `ultimo_uso_en` aproxima el momento de cierre: una sesión revocada se usó por última vez
    minutos antes, y una expirada deja de usarse al vencer.
    """
    resultado = session.execute(
        text(
            "DELETE FROM sesiones_activas "
            "WHERE estado IN ('REVOCADA', 'EXPIRADA') "
            "AND ultimo_uso_en < CURRENT_TIMESTAMP - make_interval(days => :dias)"
        ),
        {"dias": DIAS_RETENCION_CERRADAS},
    )
    return resultado.rowcount


def ejecutar(session: Session) -> tuple[int, int]:
    expiradas = marcar_expiradas(session)
    borradas = borrar_cerradas_antiguas(session)
    return expiradas, borradas


def main() -> None:
    if not settings.database_admin_url:
        raise SystemExit("Falta DATABASE_ADMIN_URL en el .env (rol app_admin)")
    engine = create_engine(
        url_con_driver_explicito(settings.database_admin_url), connect_args={"sslmode": "require"}
    )
    with Session(engine) as session, session.begin():
        expiradas, borradas = ejecutar(session)
    print(f"Sesiones marcadas como expiradas: {expiradas}. Sesiones cerradas antiguas borradas: {borradas}.")


if __name__ == "__main__":
    main()
