import http.client
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse

import pytest

BASE_URL = "http://localhost:5000"
BASE_URL_MOCK = "http://localhost:9090"
DEFAULT_TIMEOUT = 2  # in secs
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


def is_safe_url(url: str) -> bool:
    """Valida que la URL apunte a un host permitido."""
    parsed = urlparse(url)
    return parsed.hostname in ALLOWED_HOSTS


@pytest.mark.api
class TestApi(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_add(self):
        url = f"{BASE_URL}/calc/add/1/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "3", "ERROR ADD")

    def test_api_multiply(self):
        url = f"{BASE_URL}/calc/multiply/6/7"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "42", "ERROR MULTIPLY")

    def test_api_divide(self):
        url = f"{BASE_URL}/calc/divide/10/2"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "5", "ERROR DIVIDE")

    def test_api_divide_by_zero(self):
        url = f"{BASE_URL}/calc/divide/10/0"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")
        try:
            _ = urlopen(url, timeout=DEFAULT_TIMEOUT)
            self.fail("Se espera HTTP 406 para división por cero")
        except HTTPError as e:
            status_code = getattr(e, "code", None)
            self.assertEqual(status_code, http.client.NOT_ACCEPTABLE, f"Se esperaba 406, recibido {status_code}")

    def test_api_sqrt(self):
        url = f"{BASE_URL_MOCK}/calc/sqrt/64"
        self.assertTrue(is_safe_url(url), f"URL no segura: {url}")
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(response.status, http.client.OK, f"Error en la petición API a {url}")
        self.assertEqual(response.read().decode(), "8", "ERROR SQRT")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
