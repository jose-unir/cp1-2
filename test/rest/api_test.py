import http.client
import unittest
from urllib.error import HTTPError  # usado solo para mantener compatibilidad en mensajes
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


def open_with_http_client(url: str) -> http.client.HTTPResponse:
    """
    Abre la URL usando http.client, evitando urlopen() y cumpliendo la validación de esquema/host.
    Devuelve el objeto HTTPResponse.
    """
    parsed = urlparse(url)
    if not (parsed.scheme in ALLOWED_SCHEMES and parsed.hostname in ALLOWED_HOSTS):
        raise ValueError(f"URL no permitida: {url}")

    port = parsed.port or (80 if parsed.scheme == "http" else 443)
    path = parsed.path or "/"

    if parsed.scheme == "http":
        conn = http.client.HTTPConnection(parsed.hostname, port, timeout=DEFAULT_TIMEOUT)
    else:
        conn = http.client.HTTPSConnection(parsed.hostname, port, timeout=DEFAULT_TIMEOUT)

    # Nota: solo GET en estas pruebas
    conn.request("GET", path)
    return conn.getresponse()


@pytest.mark.api
class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_add(self):
        url = f"{BASE_URL}/calc/add/1/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "3", "ERROR ADD")

    def test_api_multiply(self):
        url = f"{BASE_URL}/calc/multiply/6/7"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "42", "ERROR MULTIPLY")

    def test_api_divide(self):
        url = f"{BASE_URL}/calc/divide/10/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "5", "ERROR DIVIDE")

    def test_api_divide_by_zero(self):
        url = f"{BASE_URL}/calc/divide/10/0"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        # En este caso, esperamos 406 NOT_ACCEPTABLE de la API
        self.assertEqual(
            response.status,
            http.client.NOT_ACCEPTABLE,
            f"Se esperaba 406, recibido {response.status}",
        )

    def test_api_sqrt(self):
        url = f"{BASE_URL_MOCK}/calc/sqrt/64"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")

        response = open_with_http_client(url)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "8", "ERROR SQRT")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
