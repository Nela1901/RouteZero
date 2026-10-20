"""La URL base del backend (la que figura en la documentación) no debe dar 404: redirige a Swagger."""


def test_la_raiz_redirige_a_la_documentacion(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/docs"


def test_la_documentacion_responde(client):
    assert client.get("/docs").status_code == 200
