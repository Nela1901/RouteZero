"""Cubre el requisito «Reflejo del estado real de expiración de sesiones» de
`specs/session-management/spec.md`: el job de mantenimiento marca EXPIRADA una sesión sin
uso reciente y borra las cerradas ya retenidas de sobra; `renovar` también aplica el mismo
tope de inactividad. Portado de `tests_manual/job_test.py`, ahora llamando `ejecutar()`
directo (misma cobertura que un endpoint, sin lanzar un subproceso aparte).
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from conftest import UID, db, login, reset_usuario_prueba
from src.auth.mantenimiento import ejecutar
from src.core.config import settings


def _estados_jobtest() -> dict:
    # `db()` de conftest devuelve una sola fila (fetchone); aquí sí hacen falta todas.
    conn = create_engine(settings.database_admin_url).connect()
    try:
        filas = conn.execute(
            text(
                "SELECT supabase_session_id, estado FROM sesiones_activas "
                "WHERE usuario_id=:uid AND supabase_session_id LIKE 'jobtest-%'"
            ),
            {"uid": UID},
        ).all()
        return dict(filas)
    finally:
        conn.close()


def test_el_job_marca_expiradas_y_borra_cerradas_antiguas():
    reset_usuario_prueba()
    casos = [
        ("jobtest-activa-8d", "ACTIVA", 8),
        ("jobtest-revocada-31d", "REVOCADA", 31),
        ("jobtest-expirada-5d", "EXPIRADA", 5),
        ("jobtest-activa-reciente", "ACTIVA", 0),
        ("jobtest-revocada-reciente", "REVOCADA", 1),
    ]
    for sid, estado, dias in casos:
        db(
            "INSERT INTO sesiones_activas (usuario_id, supabase_session_id, estado, ultimo_uso_en) "
            "VALUES (%s, %s, %s, CURRENT_TIMESTAMP - make_interval(days => %s))",
            (UID, sid, estado, dias),
        )

    engine = create_engine(settings.database_admin_url)
    with Session(engine) as session, session.begin():
        ejecutar(session)

    e = _estados_jobtest()
    assert e.get("jobtest-activa-8d") == "EXPIRADA"  # sin uso hace más de la vigencia del refresh (7 d)
    assert "jobtest-revocada-31d" not in e  # cerrada hace más de la retención (30 d) -> borrada
    assert e.get("jobtest-expirada-5d") == "EXPIRADA"  # ya estaba expirada, dentro de la retención
    assert e.get("jobtest-activa-reciente") == "ACTIVA"
    assert e.get("jobtest-revocada-reciente") == "REVOCADA"  # cerrada hace poco, se conserva

    reset_usuario_prueba()


def test_renovar_rechaza_una_sesion_inactiva_mas_de_7_dias(client):
    reset_usuario_prueba()
    a = login(client, "Dev-Job").json()
    db(
        "UPDATE sesiones_activas SET ultimo_uso_en = CURRENT_TIMESTAMP - interval '8 days' "
        "WHERE usuario_id=%s",
        (UID,),
    )

    r = client.post(
        "/api/auth/sesiones/renovar",
        json={"access_token": a["access_token"], "refresh_token": a["refresh_token"]},
    )
    assert r.status_code == 401
    assert "inactividad" in r.text

    estado = db("SELECT estado FROM sesiones_activas WHERE usuario_id=%s", (UID,), fetch=True)
    assert estado[0] == "EXPIRADA"

    reset_usuario_prueba()
