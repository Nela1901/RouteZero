"""Suite de la capability `mfa-totp`: inscripción, confirmación, verificación durante el
login en dos pasos y desactivación. Cada verificación TOTP consume el código de su ventana
de 30 s, así que se espera a la siguiente ventana antes de generar uno nuevo (igual que hacía
`tests_manual/e2e_sesiones.py`, del que se portó este flujo).
"""

from conftest import (
    PASSWORD,
    UID,
    auth,
    db,
    esperar_siguiente_ventana_totp,
    get,
    login,
    reset_usuario_prueba,
    totp,
)

estado: dict = {}


def test_inscribir_mfa_devuelve_factor_qr_y_secreto(client):
    reset_usuario_prueba()
    m = login(client, "Dev-M").json()
    estado["login_inicial"] = m

    r = client.post("/api/auth/mfa/inscribir", headers=auth(m["access_token"]))
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["factor_id"]
    assert cuerpo["qr_code"]
    assert cuerpo["secret"]
    estado["inscripcion"] = cuerpo


def test_bloqueo_tras_tres_codigos_invalidos_en_confirmacion(client):
    """Cubre a la vez «Código de confirmación inválido» (cada 400 individual) y «Bloqueo tras
    intentos fallidos de MFA» (el 4.º intento, aunque llegue con el código correcto, da 429)."""
    m = estado["login_inicial"]
    insc = estado["inscripcion"]

    for _ in range(3):
        r = client.post(
            "/api/auth/mfa/confirmar",
            headers=auth(m["access_token"]),
            json={"factor_id": insc["factor_id"], "codigo": "000000"},
        )
        assert r.status_code == 400

    r = client.post(
        "/api/auth/mfa/confirmar",
        headers=auth(m["access_token"]),
        json={"factor_id": insc["factor_id"], "codigo": totp(insc["secret"])},
    )
    assert r.status_code == 429
    assert db("SELECT mfa_activo FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0] is False

    # Se limpia el contador (independiente del de contraseña, RN-001) para poder confirmar de
    # verdad en la siguiente prueba, sin tocar la sesión ni el token_version.
    db("UPDATE usuarios SET mfa_intentos_fallidos=0, mfa_bloqueado_hasta=NULL WHERE usuario_id=%s", (UID,))


def test_confirmar_con_codigo_valido_activa_mfa(client):
    m = estado["login_inicial"]
    insc = estado["inscripcion"]

    r = client.post(
        "/api/auth/mfa/confirmar",
        headers=auth(m["access_token"]),
        json={"factor_id": insc["factor_id"], "codigo": totp(insc["secret"])},
    )
    assert r.status_code == 204
    assert db("SELECT mfa_activo FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0] is True


def test_la_sesion_aal1_previa_ya_no_sirve_con_mfa_activo(client):
    assert get(client, "/api/auth/me", estado["login_inicial"]["access_token"]).status_code == 401


def test_login_con_mfa_activo_devuelve_mfa_required(client):
    esperar_siguiente_ventana_totp()
    r = login(client, "Dev-M2")
    cuerpo = r.json()
    assert r.status_code == 200
    assert cuerpo["estado"] == "mfa_required"
    assert cuerpo["mfa_token"]
    assert cuerpo["factor_id"]
    assert not cuerpo.get("refresh_token")
    estado["paso1"] = cuerpo


def test_el_token_parcial_de_mfa_no_sirve_para_la_api(client):
    assert get(client, "/api/auth/me", estado["paso1"]["mfa_token"]).status_code == 401


def test_login_mfa_con_codigo_incorrecto(client):
    r = client.post(
        "/api/auth/login/mfa",
        headers=auth(estado["paso1"]["mfa_token"]),
        json={"factor_id": estado["paso1"]["factor_id"], "codigo": "000000"},
    )
    assert r.status_code == 400


def test_login_mfa_con_codigo_correcto_entrega_sesion_aal2(client):
    insc = estado["inscripcion"]
    r = client.post(
        "/api/auth/login/mfa",
        headers={**auth(estado["paso1"]["mfa_token"]), "User-Agent": "Dev-M2"},
        json={"factor_id": estado["paso1"]["factor_id"], "codigo": totp(insc["secret"])},
    )
    cuerpo = r.json()
    assert r.status_code == 200
    assert cuerpo["estado"] == "ok"
    estado["paso2"] = cuerpo

    assert get(client, "/api/auth/me", cuerpo["access_token"]).status_code == 200
    sesiones = get(client, "/api/auth/sesiones", cuerpo["access_token"]).json()
    assert any(s["dispositivo_info"] == "Dev-M2" and s["actual"] for s in sesiones)


def test_inscribir_de_nuevo_con_mfa_activo_da_409(client):
    r = client.post("/api/auth/mfa/inscribir", headers=auth(estado["paso2"]["access_token"]))
    assert r.status_code == 409


def test_desactivar_con_password_incorrecta_no_desactiva(client):
    insc = estado["inscripcion"]
    r = client.post(
        "/api/auth/mfa/desactivar",
        headers=auth(estado["paso2"]["access_token"]),
        # La contraseña se valida antes que el código TOTP (service_mfa.desactivar), así que
        # un código cualquiera basta para probar el rechazo sin gastar una ventana TOTP real.
        json={"factor_id": insc["factor_id"], "password": "contraseña-incorrecta", "codigo": "000000"},
    )
    assert r.status_code == 400
    assert db("SELECT mfa_activo FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0] is True


def test_desactivar_mfa_requiere_password_y_codigo_validos(client):
    insc = estado["inscripcion"]
    esperar_siguiente_ventana_totp()

    r = client.post(
        "/api/auth/mfa/desactivar",
        headers=auth(estado["paso2"]["access_token"]),
        json={"factor_id": insc["factor_id"], "password": PASSWORD, "codigo": totp(insc["secret"])},
    )
    assert r.status_code == 204
    assert db("SELECT mfa_activo FROM usuarios WHERE usuario_id=%s", (UID,), fetch=True)[0] is False
    reset_usuario_prueba()
