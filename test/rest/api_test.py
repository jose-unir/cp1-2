
import http.client
import ssl
import unittest
from urllib.parse import urlparse
import pytest

BASE_URL = "http://localhost:5000"
BASE_URL_MOCK = "http://localhost:9090"
DEFAULT_TIMEOUT = 2  # seconds

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


def is_safe_url(url: str) -> bool:
    """Valida que la URL tenga esquema y host permitidos."""
    parsed = urlparse(url)
    return parsed.scheme in ALLOWED_SCHEMES and parsed.hostname in ALLOWED_HOSTS


def _build_request_target(parsed) -> str:
    """
    Construye el objetivo de la petición (path + query).
    El fragmento (#...) no viaja en HTTP, así que se ignora.
    """
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return path


def open_with_http_client(url: str) -> http.client.HTTPResponse:
    """
    Abre la URL usando http.client, evitando urlopen() y cumpliendo la validación de esquema/host.
    Devuelve el objeto HTTPResponse. La conexión se cierra automáticamente si ocurre una excepción.
    """
    parsed = urlparse(url)
    if not (parsed.scheme in ALLOWED_SCHEMES and parsed.hostname in ALLOWED_HOSTS):
        raise ValueError(f"URL no permitida: {url}")

    port = parsed.port or (80 if parsed.scheme == "http" else 443)
    target = _build_request_target(parsed)

    if parsed.scheme == "http":
        conn = http.client.HTTPConnection(parsed.hostname, port, timeout=DEFAULT_TIMEOUT)
    else:
        # Contexto seguro para HTTPS (Python 3.12 ya verifica por defecto, esto lo refuerza)
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        conn = http.client.HTTPSConnection(parsed.hostname, port, timeout=DEFAULT_TIMEOUT, context=ctx)

    try:
        # Nota: solo GET en estas pruebas
        conn.request("GET", target)
        resp = conn.getresponse()
        return resp
    except Exception:
        # Asegura cierre en caso de error
        conn.close()
        raise


@pytest.mark.api
class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_add(self):
        url = f"{BASE_URL}/calc/add/1/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        try:
            self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
            body = response.read().decode()
            self.assertEqual(body, "3", "ERROR ADD")
        finally:
            response.close()

    def test_api_multiply(self):
        url = f"{BASE_URL}/calc/multiply/6/7"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        try:
            self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
            body = response.read().decode()
            self.assertEqual(body, "42", "ERROR MULTIPLY")
        finally:
            response.close()

    def test_api_divide(self):
        url = f"{BASE_URL}/calc/divide/10/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        try:
            self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
            body = response.read().decode()
            self.assertEqual(body, "5", "ERROR DIVIDE")
        finally:
            response.close()

    def test_api_divide_by_zero(self):
        url = f"{BASE_URL}/calc/divide/10/0"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        try:
            # En este caso, esperamos 406 NOT_ACCEPTABLE de la API
            self.assertEqual(
                response.status,
                http.client.NOT_ACCEPTABLE,
                f"Se esperaba 406, recibido {response.status}",
            )
            # Opcional: leer y descartar cuerpo si la API devuelve mensaje
            _ = response.read()
        finally:
            response.close()

    def test_api_sqrt(self):
        url = f"{BASE_URL_MOCK}/calc/sqrt/64"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        try:
            self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
            body = response.read().decode()
            self.assertEqual(body, "8", "ERROR SQRT")
        finally:
            response.close()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
