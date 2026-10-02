"""Prueba explícita de inyección SQL (HT-01, OWASP Top 10 — A03:2021 Injection).

No es un análisis estático: son payloads clásicos de inyección enviados de verdad contra
endpoints reales, con SQLAlchemy conectado a Supabase, para comprobar que el bind de
parámetros los trata como texto literal y no como SQL ejecutable.
"""

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

PAYLOADS_CLASICOS = [
    "Robert'); DROP TABLE clientes;--",
    "' OR '1'='1",
    "'; UPDATE usuarios SET rol_id = NULL; --",
    "admin'--",
]


def _tabla_existe(nombre: str) -> bool:
    fila = admin_db("SELECT to_regclass(%s)", (f"public.{nombre}",), fetch=True)
    return fila[0][0] is not None


def test_payload_en_nombre_de_cliente_se_guarda_como_texto_literal(client):
    operador = login(client, "Dev-Injection", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()
    payload = PAYLOADS_CLASICOS[0]

    r = client.post(
        "/api/clientes",
        headers=auth(operador["access_token"]),
        json={
            "nombre": payload,
            "tipo_negocio": "OTRO",
            "latitud": "-12.0653",
            "longitud": "-75.2049",
        },
    )

    assert r.status_code == 201  # se acepta como dato, no se interpreta como SQL
    cuerpo = r.json()
    assert cuerpo["nombre"] == payload  # se guardó tal cual, ni truncado ni alterado
    assert _tabla_existe("clientes")  # la tabla del "DROP TABLE" sigue intacta

    admin_db("DELETE FROM clientes WHERE cliente_id = %s", (cuerpo["cliente_id"],))


def test_payload_en_descripcion_de_pedido_no_ejecuta_sql(client):
    operador = login(client, "Dev-Injection", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()
    cliente = client.post(
        "/api/clientes",
        headers=auth(operador["access_token"]),
        json={"nombre": "Cliente de prueba", "tipo_negocio": "OTRO", "latitud": "-12.0653", "longitud": "-75.2049"},
    ).json()

    payload = PAYLOADS_CLASICOS[2]
    r = client.post(
        "/api/pedidos",
        headers=auth(operador["access_token"]),
        json={
            "cliente_id": cliente["cliente_id"],
            "descripcion": payload,
            "peso_kg": "5.00",
            "latitud": "-12.0653",
            "longitud": "-75.2049",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )

    assert r.status_code == 201
    assert r.json()["descripcion"] == payload
    assert _tabla_existe("usuarios")  # el intento de vaciar usuarios.rol_id no corrió

    admin_db("DELETE FROM pedidos WHERE cliente_id = %s", (cliente["cliente_id"],))
    admin_db("DELETE FROM clientes WHERE cliente_id = %s", (cliente["cliente_id"],))


def test_payload_clasico_en_el_login_no_da_bypass(client):
    for payload in PAYLOADS_CLASICOS:
        r = login(client, "Dev-Injection", email="ataque@routezero.dev", password=payload)
        # Nunca 200: ni error de servidor (SQL roto) ni acceso indebido (bypass de auth).
        assert r.status_code in (401, 422), f"{payload!r} dio {r.status_code}"

    for payload in PAYLOADS_CLASICOS:
        r = login(client, "Dev-Injection", email=payload, password="cualquiera")
        assert r.status_code in (401, 422), f"{payload!r} dio {r.status_code}"


def test_payload_con_arroba_llega_a_la_busqueda_sql_por_correo_sin_bypass(client):
    """A diferencia de los payloads de arriba (sin "@", los rechaza Pydantic antes de tocar
    SQL), este sí pasa la validación de formato y llega hasta `usuario_id_por_email`
    (la función SQL parametrizada que busca en auth.users) — es el que de verdad ejercita
    esa capa contra inyección (el payload no lleva espacios: el formato de correo los
    rechaza de todas formas, y eso taparía la prueba real de SQL con un simple 422)."""
    payload = "x'or'1'='1'--@routezero.dev"
    r = login(client, "Dev-Injection", email=payload, password="cualquiera")
    assert r.status_code == 401
    assert "Credenciales inválidas" in r.text
