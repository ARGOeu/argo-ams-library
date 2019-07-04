import unittest
from pymod import ArgoMessagingService
from pymod import AmsServiceException
from httmock import urlmatch, HTTMock, response


class TestAuthenticate(unittest.TestCase):
    #TODO
    # temporarily ignore this test case because build tool uses 2.4.3 reqests, which handles invalid cert files differently
    # tests the case of providing wrong file path for cert
    # def test_auth_via_cert_invalid_cert(self):
    #
    #     try:
    #         _ = ArgoMessagingService(endpoint="localhost", project="TEST", cert="/cert/path")
    #     except Exception as e:
    #         # self.assertEqual(e.message, "Could not find the TLS certificate file, invalid path: /cert/path")
    #         self.assertIsInstance(e, IOError)
    #
    # # tests the case of providing wrong file path for key
    # def test_auth_via_cert_invalid_key(self):
    #
    #     try:
    #         _ = ArgoMessagingService(endpoint="localhost", project="TEST", key="/cert/key")
    #     except Exception as e:
    #         self.assertEqual(e.message, "Could not find the TLS key file, invalid path: /cert/key")
    #         self.assertIsInstance(e, IOError)

    # tests the case of providing empty arguments for the cert and key
    def test_auth_via_cert_cert(self):

        try:
            ams = ArgoMessagingService(endpoint="localhost", token="s3cret", project="TEST")
            ams.auth_via_cert("","")
        except AmsServiceException as e:
            self.assertEqual(e.code, 400)
            self.assertEqual(e.msg, 'While trying the [auth_x509]: No certificate provided.')

    # tests the case of providing empty arguments for token and cert
    def test_auth_via_cert_empty_token_and_cert(self):

        try:
            ams = ArgoMessagingService(endpoint="localhost", project="TEST")
        except AmsServiceException as e:
            self.assertEqual(e.code, 400)
            self.assertEqual(e.msg, 'While trying the [auth_x509]: No certificate provided. No token provided')

    # tests the case of providing a token
    def test_assign_token(self):
        ams = ArgoMessagingService(endpoint="localhost", token="some_token", project="TEST")
        self.assertEqual(ams.token, "some_token")

    # tests the successful retrieval of a token
    def test_auth_via_cert_success(self):

        auth_via_cert_urlmatch = dict(netloc="localhost",
                                      path="/v1/service-types/ams/hosts/localhost:authx509",
                                      method='GET')

        # Mock response for successful token retrieval
        @urlmatch(**auth_via_cert_urlmatch)
        def auth_via_cert_success(url, request):
            assert url.path == "/v1/service-types/ams/hosts/localhost:authx509"
            return response(200, '{"token":"success_token"}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(auth_via_cert_success):
            ams = ArgoMessagingService(endpoint="localhost", project="TEST", cert="/path/cert", key="/path/key")
            self.assertEqual(ams.token, "success_token")

    # tests the case where the response doesn't contain the `token` field
    def test_auth_via_cert_missing_token_field(self):

        auth_via_cert_urlmatch = dict(netloc="localhost",
                                      path="/v1/service-types/ams/hosts/localhost:authx509",
                                      method='GET')

        # Mock response for successful token retrieval
        @urlmatch(**auth_via_cert_urlmatch)
        def auth_via_cert_missing_field(url, request):
            assert url.path == "/v1/service-types/ams/hosts/localhost:authx509"
            return response(200, '{"other_field":"success_token"}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(auth_via_cert_missing_field):
            try:
                ams = ArgoMessagingService(endpoint="localhost", project="TEST", cert="/path/cert", key="/path/key")
                ams.auth_via_cert("/path/cert", "/path/key")
            except AmsServiceException as e:
                self.assertEqual(e.code, 500)
                self.assertEqual(e.msg, "While trying the [auth_x509]: Token was not found in the response.Response: {u'other_field': u'success_token'}")

if __name__ == "__main__":
    unittest.main()
