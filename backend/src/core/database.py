from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings


def url_con_driver_explicito(url: str) -> str:
    """Fuerza el driver `psycopg2` (el que está en requirements.txt) en la URL que recibe
    SQLAlchemy, en vez de dejarlo adivinar uno. Una URL `postgresql://` sin driver explícito
    puede resolver a `psycopg` (v3, no instalado) según la versión de SQLAlchemy instalada
    — pasó así en Render con una versión más nueva que la usada en desarrollo local, aunque
    la misma URL funcionaba ahí sin problema. Solo se usa para crear el engine: `settings.*`
    se deja intacto porque scripts de prueba y mantenimiento conectan con `psycopg2.connect()`
    directo, que no entiende el sufijo `+psycopg2` de SQLAlchemy."""
    if not url or "+" in url.split("://", 1)[0]:
        return url
    return url.replace("postgresql://", "postgresql+psycopg2://", 1).replace(
        "postgres://", "postgresql+psycopg2://", 1
    )


engine = create_engine(
    url_con_driver_explicito(settings.database_url),
    pool_pre_ping=True,
    # Supabase ya exige TLS del lado del servidor (comprobado: TLSv1.3), pero se declara
    # explícito aquí para que la conexión falle en vez de degradar en silencio si alguna
    # vez apunta a un host que no lo exija (RN-013 / Ley N° 29733, cifrado en tránsito).
    connect_args={"sslmode": "require"},
)
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
