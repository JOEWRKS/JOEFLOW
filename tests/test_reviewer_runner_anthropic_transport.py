import inspect
import socket
import ssl
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.backend import BackendInvocationError

try:
    from reviewer_runner.providers.anthropic import (
        ANTHROPIC_API_VERSION,
        ANTHROPIC_HOST,
        ANTHROPIC_MAX_RESPONSE_BYTES,
        ANTHROPIC_PATH,
        AnthropicHttpResponse,
        StdlibAnthropicTransport,
    )
except ImportError:
    ANTHROPIC_API_VERSION = None
    ANTHROPIC_HOST = None
    ANTHROPIC_MAX_RESPONSE_BYTES = None
    ANTHROPIC_PATH = None
    AnthropicHttpResponse = None
    StdlibAnthropicTransport = None


class _FakeResponse:
    def __init__(self, *, status=200, headers=(), body=b"{}", read_error=None):
        self.status = status
        self._headers = headers
        self._body = body
        self._read_error = read_error
        self.read_sizes = []

    def getheaders(self):
        return self._headers

    def read(self, amount=-1):
        self.read_sizes.append(amount)
        if self._read_error is not None:
            raise self._read_error
        return self._body


class _FakeConnection:
    def __init__(self, response=None, *, request_error=None, response_error=None):
        self.response = response or _FakeResponse()
        self.request_error = request_error
        self.response_error = response_error
        self.request_calls = []
        self.getresponse_calls = 0
        self.close_calls = 0

    def request(self, method, path, body=None, headers=None):
        self.request_calls.append((method, path, body, headers))
        if self.request_error is not None:
            raise self.request_error

    def getresponse(self):
        self.getresponse_calls += 1
        if self.response_error is not None:
            raise self.response_error
        return self.response

    def close(self):
        self.close_calls += 1


class _FakeConnectionFactory:
    def __init__(self, connection):
        self.connection = connection
        self.calls = []

    def __call__(self, host, port, timeout, context):
        self.calls.append((host, port, timeout, context))
        return self.connection


class ReviewerRunnerAnthropicTransportTests(unittest.TestCase):
    def require_transport(self):
        self.assertIsNotNone(StdlibAnthropicTransport)
        self.assertIsNotNone(AnthropicHttpResponse)
        return StdlibAnthropicTransport

    def _transport(self, connection):
        transport_type = self.require_transport()
        if transport_type is None:
            return None, None
        factory = _FakeConnectionFactory(connection)
        return transport_type(test_only_connection_factory=factory), factory

    def _post(self, connection, *, body=b'{"request":true}', timeout_seconds=7):
        transport, factory = self._transport(connection)
        if transport is None:
            return None, factory
        return transport.post(
            body,
            api_key="test-only-anthropic-key",
            timeout_seconds=timeout_seconds,
        ), factory

    def test_default_transport_uses_fresh_https_connection_verified_default_context_and_fixed_host(self):
        transport_type = self.require_transport()
        if transport_type is None:
            return
        first = _FakeConnection()
        second = _FakeConnection()
        connections = [first, second]
        constructor_calls = []
        original_context = ssl.create_default_context

        def tracked_context(*args, **kwargs):
            context = original_context(*args, **kwargs)
            constructor_calls.append(context)
            return context

        class FakeHttpsConnection:
            def __init__(self, host, port=None, timeout=None, context=None):
                self.delegate = connections.pop(0)
                self.args = (host, port, timeout, context)
                FakeHttpsConnection.instances.append(self)

            def request(self, *args, **kwargs):
                return self.delegate.request(*args, **kwargs)

            def getresponse(self):
                return self.delegate.getresponse()

            def close(self):
                return self.delegate.close()

        FakeHttpsConnection.instances = []
        import reviewer_runner.providers.anthropic as anthropic_module
        original_https_connection = anthropic_module.http.client.HTTPSConnection
        anthropic_module.ssl.create_default_context = tracked_context
        anthropic_module.http.client.HTTPSConnection = FakeHttpsConnection
        try:
            transport = transport_type()
            transport.post(b"one", api_key="test-only-anthropic-key", timeout_seconds=3)
            transport.post(b"two", api_key="test-only-anthropic-key", timeout_seconds=5)
        finally:
            anthropic_module.ssl.create_default_context = original_context
            anthropic_module.http.client.HTTPSConnection = original_https_connection

        self.assertEqual(len(constructor_calls), 2)
        self.assertEqual(len(FakeHttpsConnection.instances), 2)
        self.assertIsNot(FakeHttpsConnection.instances[0], FakeHttpsConnection.instances[1])
        self.assertEqual(
            [item.args[:3] for item in FakeHttpsConnection.instances],
            [("api.anthropic.com", 443, 3), ("api.anthropic.com", 443, 5)],
        )
        self.assertTrue(all(item.args[3].check_hostname for item in FakeHttpsConnection.instances))
        self.assertTrue(all(item.args[3].verify_mode == ssl.CERT_REQUIRED for item in FakeHttpsConnection.instances))

    def test_exact_post_path_headers_body_and_connection_close(self):
        connection = _FakeConnection(response=_FakeResponse(headers=(("request-id", "req-1"),)))
        result, factory = self._post(connection, body=b'{"exact":true}')
        if result is None:
            return
        self.assertIsInstance(result, AnthropicHttpResponse)
        self.assertEqual(len(factory.calls), 1)
        self.assertEqual(connection.request_calls, [
            (
                "POST",
                "/v1/messages",
                b'{"exact":true}',
                {
                    "anthropic-version": "2023-06-01",
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": "test-only-anthropic-key",
                },
            )
        ])
        self.assertEqual(connection.close_calls, 1)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.headers, (("request-id", "req-1"),))
        self.assertEqual(result.body, b"{}")

    def test_success_performs_one_request_and_closes_connection(self):
        connection = _FakeConnection(response=_FakeResponse(body=b'{"ok":true}'))
        result, factory = self._post(connection)
        if result is None:
            return
        self.assertEqual(result.body, b'{"ok":true}')
        self.assertEqual(len(factory.calls), 1)
        self.assertEqual(len(connection.request_calls), 1)
        self.assertEqual(connection.getresponse_calls, 1)
        self.assertEqual(connection.response.read_sizes, [16_777_217])
        self.assertEqual(connection.close_calls, 1)

    def test_redirect_408_409_429_and_5xx_fail_without_second_request(self):
        for status in (301, 302, 307, 308, 408, 409, 429, 500, 503):
            with self.subTest(status=status):
                connection = _FakeConnection(response=_FakeResponse(status=status, body=b"must-not-leak"))
                with self.assertRaises(BackendInvocationError) as raised:
                    self._post(connection)
                self.assertEqual(raised.exception.code, "NO_RESPONSE")
                self.assertNotIn("must-not-leak", str(raised.exception))
                self.assertEqual(len(connection.request_calls), 1)
                self.assertEqual(connection.getresponse_calls, 1)
                self.assertEqual(connection.close_calls, 1)

    def test_timeout_eof_tls_and_connection_loss_fail_without_retry(self):
        import http.client
        cases = (
            ("timeout", socket.timeout(), "TIMEOUT", "request"),
            ("tls", ssl.SSLError("test tls failure"), "TRANSPORT_ERROR", "request"),
            ("connection-loss", ConnectionResetError(), "TRANSPORT_ERROR", "request"),
            ("eof-before-response", http.client.RemoteDisconnected("test eof"), "TRANSPORT_ERROR", "response"),
            ("incomplete-response", http.client.IncompleteRead(b"partial"), "NO_RESPONSE", "read"),
        )
        for label, error, expected_code, phase in cases:
            with self.subTest(label=label):
                if phase == "request":
                    connection = _FakeConnection(request_error=error)
                elif phase == "response":
                    connection = _FakeConnection(response_error=error)
                else:
                    connection = _FakeConnection(response=_FakeResponse(read_error=error))
                with self.assertRaises(BackendInvocationError) as raised:
                    self._post(connection)
                self.assertEqual(raised.exception.code, expected_code)
                self.assertNotIn("test tls failure", str(raised.exception))
                self.assertNotIn("partial", str(raised.exception))
                self.assertEqual(len(connection.request_calls), 1)
                self.assertEqual(connection.close_calls, 1)

    def test_oversized_or_incomplete_response_fails_closed(self):
        oversized = _FakeConnection(response=_FakeResponse(body=b"x" * 16_777_217))
        with self.assertRaises(BackendInvocationError) as raised:
            self._post(oversized)
        self.assertEqual(raised.exception.code, "NO_RESPONSE")
        self.assertEqual(oversized.response.read_sizes, [16_777_217])
        self.assertEqual(oversized.close_calls, 1)

        incomplete = _FakeConnection(response=_FakeResponse(read_error=EOFError("truncated")))
        with self.assertRaises(BackendInvocationError) as raised:
            self._post(incomplete)
        self.assertEqual(raised.exception.code, "NO_RESPONSE")
        self.assertEqual(len(incomplete.request_calls), 1)
        self.assertEqual(incomplete.close_calls, 1)

    def test_proxy_environment_is_not_consulted_and_caller_url_is_impossible(self):
        transport_type = self.require_transport()
        if transport_type is None:
            return
        source = inspect.getsource(sys.modules[transport_type.__module__])
        self.assertNotIn("proxy", source.lower())
        self.assertNotIn("urllib", source.lower())
        parameter_names = tuple(inspect.signature(transport_type.post).parameters)
        self.assertEqual(parameter_names, ("self", "body", "api_key", "timeout_seconds"))
        self.assertNotIn("url", parameter_names)
        self.assertNotIn("host", parameter_names)
        self.assertNotIn("path", parameter_names)

    def test_custom_transport_factory_is_marked_test_only(self):
        transport_type = self.require_transport()
        if transport_type is None:
            return
        production = transport_type()
        custom, _ = self._transport(_FakeConnection())
        self.assertFalse(production.is_test_double)
        self.assertTrue(custom.is_test_double)
        initializer_names = tuple(inspect.signature(transport_type).parameters)
        self.assertEqual(initializer_names, ("test_only_connection_factory",))


if __name__ == "__main__":
    unittest.main()
