"""Suite de la capability `session-management`: login sin MFA, renovación, detección de
reuso de refresh token, bloqueo por intentos fallidos (RN-001) y revocación de sesiones.

Las pruebas de un mismo bloque dependen entre sí a propósito (igual que el flujo real de un
usuario) y se ejecutan en el orden en que aparecen en el archivo; `reset_usuario_prueba()`
deja la cuenta en un estado conocido entre bloques.
"""

import time
import uuid

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, UID, admin_db, auth, db, get, login, reset_usuario_prueba

estado: dict = {}


def test_login_sin_mfa_devuelve_tokens(client):
    reset_usuario_prueba()
    r = login(client, "Dev-A")
    cuerpo = r.json()
    assert r.status_code == 200
    assert cuerpo["estado"] == "ok"
    assert cuerpo["access_token"]
    assert cuerpo["refresh_token"]
    estado["A"] = cuerpo


def test_me_con_el_token_recien_emitido(client):
    assert get(client, "/api/auth/me", estado["A"]["access_token"]).status_code == 200


def test_me_sin_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_con_token_falso(client):
    assert get(client, "/api/auth/me", "token-que-no-existe").status_code == 401


def test_listado_muestra_una_sesion_actual_con_su_dispositivo(client):
    lista = get(client, "/api/auth/sesiones", estado["A"]["access_token"]).json()
    assert len(lista) == 1
    assert lista[0]["actual"] is True
    assert lista[0]["dispositivo_info"] == "Dev-A"


def test_renovar_devuelve_tokens_nuevos_y_validos(client):
    r = client.post(
        "/api/auth/sesiones/renovar",
        json={"access_token": estado["A"]["access_token"], "refresh_token": estado["A"]["refresh_token"]},
    )
    cuerpo = r.json()
    assert r.status_code == 200
    assert cuerpo["estado"] == "ok"
    estado["A2"] = cuerpo
    assert get(client, "/api/auth/me", estado["A2"]["access_token"]).status_code == 200
    assert len(get(client, "/api/auth/sesiones", estado["A2"]["access_token"]).json()) == 1


def test_renovar_con_el_refresh_anterior_dentro_de_la_ventana_de_gracia(client):
    """Un reintento con el refresh token justo rotado no se penaliza (decisión 5 de design.md)."""
    r = client.post(
        "/api/auth/sesiones/renovar",
        json={"access_token": estado["A2"]["access_token"], "refresh_token": estado["A"]["refresh_token"]},
    )
    assert r.status_code == 200


def test_renovar_con_refresh_token_desconocido_no_toca_la_sesion(client):
    r = client.post(
        "/api/auth/sesiones/renovar",
        json={"access_token": estado["A2"]["access_token"], "refresh_token": "tokenbasura123456"},
    )
    assert r.status_code == 401
    assert get(client, "/api/auth/me", estado["A2"]["access_token"]).status_code == 200


def test_reuso_del_refresh_token_fuera_de_la_ventana_revoca_la_sesion(client):
    time.sleep(12)  # fuera de la ventana de tolerancia de reuso de Supabase (10 s)
    r = client.post(
        "/api/auth/sesiones/renovar",
        json={"access_token": estado["A2"]["access_token"], "refresh_token": estado["A"]["refresh_token"]},
    )
    assert r.status_code == 401
    assert get(client, "/api/auth/me", estado["A2"]["access_token"]).status_code == 401
    # No se incrementa token_version (IMP-006): ver test_cerrar_todas_las_sesiones_invalida_todos_los_tokens.
    version = db("SELECT token_version FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0]
    assert version == 1
    reset_usuario_prueba()


def test_bloqueo_tras_tres_intentos_fallidos(client):
    codigos = [login(client, "Dev-X", password="incorrecta").status_code for _ in range(3)]
    assert codigos == [401, 401, 401]

    r = login(client, "Dev-X")  # la cuarta vez, ya con la contraseña correcta
    assert r.status_code == 429
    assert "segundos" in r.text
    reset_usuario_prueba()


def test_correo_inexistente_da_el_mismo_401_generico(client):
    r = login(client, "Dev-X", email="noexiste@routezero.dev")
    assert r.status_code == 401
    assert "Credenciales inválidas" in r.text


def test_revocar_otro_dispositivo_de_la_misma_cuenta_lo_invalida(client):
    reset_usuario_prueba()
    a = login(client, "Dev-A").json()
    b = login(client, "Dev-B").json()

    lista = get(client, "/api/auth/sesiones", a["access_token"]).json()
    assert len(lista) == 2
    otra = next(s for s in lista if not s["actual"])

    r = client.delete(f"/api/auth/sesiones/{otra['sesion_id']}", headers=auth(a["access_token"]))
    assert r.status_code == 204
    assert get(client, "/api/auth/me", b["access_token"]).status_code == 401
    assert len(get(client, "/api/auth/sesiones", a["access_token"]).json()) == 1
    estado["a_propia"] = a


def test_revocar_una_sesion_inexistente_da_404(client):
    r = client.delete(f"/api/auth/sesiones/{uuid.uuid4()}", headers=auth(estado["a_propia"]["access_token"]))
    assert r.status_code == 404


def test_revocar_sesion_de_otra_cuenta_da_404_no_403(client):
    """RLS solo deja ver las sesiones propias: una ajena se ve igual que una inexistente,
    así que ni siquiera se distingue "existe pero no es tuya" con un 403 aparte."""
    operador = login(client, "Dev-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()
    sesion_operador = next(
        s for s in get(client, "/api/auth/sesiones", operador["access_token"]).json() if s["actual"]
    )

    r = client.delete(
        f"/api/auth/sesiones/{sesion_operador['sesion_id']}", headers=auth(estado["a_propia"]["access_token"])
    )
    assert r.status_code == 404
    assert get(client, "/api/auth/me", operador["access_token"]).status_code == 200  # sigue viva

    admin_db("DELETE FROM sesiones_activas WHERE sesion_id = %s", (sesion_operador["sesion_id"],))


def test_cerrar_la_propia_sesion_la_invalida(client):
    propia = next(
        s for s in get(client, "/api/auth/sesiones", estado["a_propia"]["access_token"]).json() if s["actual"]
    )
    r = client.delete(f"/api/auth/sesiones/{propia['sesion_id']}", headers=auth(estado["a_propia"]["access_token"]))
    assert r.status_code == 204
    assert get(client, "/api/auth/me", estado["a_propia"]["access_token"]).status_code == 401


def test_cerrar_todas_las_sesiones_invalida_todos_los_tokens(client):
    reset_usuario_prueba()
    c1 = login(client, "Dev-C1").json()
    c2 = login(client, "Dev-C2").json()

    r = client.delete("/api/auth/sesiones", headers=auth(c1["access_token"]))
    assert r.status_code == 204
    assert get(client, "/api/auth/me", c1["access_token"]).status_code == 401
    assert get(client, "/api/auth/me", c2["access_token"]).status_code == 401

    # No se incrementa token_version (IMP-006): el Custom Access Token Hook de Supabase lo
    # cacheaba y bloqueaba logins nuevos legítimos. La invalidación de arriba ya depende solo
    # de sesiones_activas.estado, sin pasar por el hook.
    version = db("SELECT token_version FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0]
    assert version == 1
    reset_usuario_prueba()
