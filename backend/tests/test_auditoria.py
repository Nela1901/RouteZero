"""Suite del módulo de auditoría (HT-01): que los eventos de seguridad queden registrados en
`logs_auditoria`, y que solo ADMINISTRADOR pueda consultarlos.
"""

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, UID, auth, db, login, reset_usuario_prueba


def _ultima_accion(accion: str) -> dict | None:
    fila = db(
        "SELECT accion, modulo, ip_origen FROM logs_auditoria "
        "WHERE usuario_id=%s AND accion=%s ORDER BY creado_en DESC LIMIT 1",
        (UID, accion),
        fetch=True,
    )
    return {"accion": fila[0], "modulo": fila[1], "ip_origen": fila[2]} if fila else None


def test_login_exitoso_queda_registrado(client):
    reset_usuario_prueba()
    login(client, "Dev-Auditoria")

    registro = _ultima_accion("login_exitoso")
    assert registro is not None
    assert registro["modulo"] == "auth"
    reset_usuario_prueba()


def test_login_fallido_queda_registrado(client):
    reset_usuario_prueba()
    login(client, "Dev-Auditoria", password="incorrecta")

    registro = _ultima_accion("login_fallido")
    assert registro is not None
    reset_usuario_prueba()


def test_solo_administrador_puede_listar_la_auditoria(client):
    admin = login(client, "Dev-Auditoria-Admin").json()
    r = client.get("/api/auditoria", headers=auth(admin["access_token"]))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    operador = login(client, "Dev-Auditoria-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()
    r = client.get("/api/auditoria", headers=auth(operador["access_token"]))
    assert r.status_code == 403

    r = client.get("/api/auditoria")
    assert r.status_code == 401

    reset_usuario_prueba()


def test_filtro_por_modulo(client):
    admin = login(client, "Dev-Auditoria-Filtro").json()
    r = client.get("/api/auditoria", headers=auth(admin["access_token"]), params={"modulo": "auth"})
    assert r.status_code == 200
    assert all(fila["modulo"] == "auth" for fila in r.json())
    reset_usuario_prueba()
