from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def sesion_como_usuario(usuario_id: str | None = None) -> Iterator[Session]:
    """Sesión de SQLAlchemy con una única transacción, con RLS fijado a `usuario_id`.

    Se usa donde no hay un token de acceso todavía (p. ej. el login, cuando el backend
    actúa de confianza sobre la cuenta que se está autenticando). Si `usuario_id` es
    None no se fija la variable y RLS no devolverá filas de tablas protegidas.

    SET LOCAL (no SET) hace que el valor viva solo en esta transacción y nunca se filtre
    a otra petición que reutilice la misma conexión del pool. Un único commit al final:
    un commit intermedio cerraría la transacción y RLS dejaría de aplicarse a lo siguiente.
    """
    session = SessionLocal()
    try:
        if usuario_id is not None:
            session.execute(
                text("SET LOCAL app.usuario_actual_id = :usuario_id"),
                {"usuario_id": usuario_id},
            )
        yield session
        session.commit()
    except HTTPException:
        # Respuesta de negocio esperada (credenciales inválidas, etc.): se conservan los
        # cambios ya hechos, p. ej. el contador de intentos fallidos.
        session.commit()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
