import datetime
import unittest

from httmock import urlmatch, response, HTTMock

from pymod import ArgoMessagingService


class TestMetrics(unittest.TestCase):

    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="TEST")

        self.version_json = """
        {
        "build_time": "2022-08-01T08:15:59Z",
        "golang": "go1.15",
        "compiler": "gc",
        "os": "linux",
        "architecture": "amd64",
        "release": "1.3.0",
        "distro": "CentOS Linux release 7.9.2009 (Core)",
        "hostname": "localhost"
        }
        """

        self.status_json = """
        {
            "status": "ok",
            "push_servers": [
                {
                    "endpoint": "push-test.argo.grnet.gr:8443",
                    "status": "SERVING"
                }
            ]
        }
        """

        self.metrics_json = """
        {
            "metrics": [
                {
                    "metric": "ams_node.cpu_usage",
                    "metric_type": "percentage",
                    "value_type": "float64",
                    "resource_type": "ams_node",
                    "resource_name": "test.argo.grnet.gr",
                    "timeseries": [
                        {
                            "timestamp": "2022-08-23T14:28:23Z",
                            "value": 34
                        }
                    ],
                    "description": "Percentage value that displays the CPU usage of ams service in the specific node"
                }
            ]
        }
        """

        self.va_metrics_json = """
        {
            "projects_metrics": {
                "projects": [
                    {
                        "project": "P1",
                        "message_count": 432148,
                        "average_daily_messages": 14404.94,
                        "topics_count": 1,
                        "subscriptions_count": 1,
                        "users_count": 2
                    },
                    {
                    "project": "P2",
                    "message_count": 15570237,
                    "average_daily_messages": 519007.9,
                    "topics_count": 1,
                    "subscriptions_count": 1,
                    "users_count": 3
                    }
                ],
                "total_message_count": 16002385,
                "average_daily_messages": 533412.84
            },
        "total_users_count": 5,
        "total_topics_count": 2,
        "total_subscriptions_count": 2
    }
    """

    version_urlmatch = dict(netloc="localhost",
                            path="/v1/version",
                            method='GET')

    status_urlmatch = dict(netloc="localhost",
                           path="/v1/status",
                           method='GET')

    metrics_urlmatch = dict(netloc="localhost",
                            path="/v1/metrics",
                            method='GET')

    va_metrics_urlmatch = dict(netloc="localhost",
                            path="/v1/metrics/va_metrics",
                            method='GET')

    def testVersion(self):
        @urlmatch(**self.version_urlmatch)
        def version_mock(url, request):
            self.assertEqual("/v1/version", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.version_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(version_mock):
            version_info = self.ams.version()
            self.assertEqual("2022-08-01T08:15:59Z", version_info["build_time"])
            self.assertEqual("go1.15", version_info["golang"])
            self.assertEqual("gc", version_info["compiler"])
            self.assertEqual("linux", version_info["os"])
            self.assertEqual("amd64", version_info["architecture"])
            self.assertEqual("1.3.0", version_info["release"])
            self.assertEqual("CentOS Linux release 7.9.2009 (Core)", version_info["distro"])
            self.assertEqual("localhost", version_info["hostname"])

    def testStatus(self):
        @urlmatch(**self.status_urlmatch)
        def status_mock(url, request):
            self.assertEqual("/v1/status", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.status_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(status_mock):
            status_info = self.ams.status()
            self.assertEqual("ok", status_info["status"])
            self.assertEqual("push-test.argo.grnet.gr:8443", status_info["push_servers"][0]["endpoint"])
            self.assertEqual("SERVING", status_info["push_servers"][0]["status"])

    def testMetrics(self):
        @urlmatch(**self.metrics_urlmatch)
        def metrics_mock(url, request):
            self.assertEqual("/v1/metrics", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.metrics_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(metrics_mock):
            metrics_info = self.ams.metrics()
            self.assertEqual("ams_node.cpu_usage", metrics_info["metrics"][0]["metric"])
            self.assertEqual("percentage", metrics_info["metrics"][0]["metric_type"])
            self.assertEqual("float64", metrics_info["metrics"][0]["value_type"])
            self.assertEqual("ams_node", metrics_info["metrics"][0]["resource_type"])
            self.assertEqual("test.argo.grnet.gr", metrics_info["metrics"][0]["resource_name"])
            self.assertEqual("Percentage value that displays the CPU usage of ams service in the specific node",
                             metrics_info["metrics"][0]["description"])
            self.assertEqual("2022-08-23T14:28:23Z", metrics_info["metrics"][0]["timeseries"][0]["timestamp"])
            self.assertEqual(34, metrics_info["metrics"][0]["timeseries"][0]["value"])

    def testVaMetrics(self):
        @urlmatch(**self.va_metrics_urlmatch)
        def va_metrics_mock(url, request):
            self.assertEqual("/v1/metrics/va_metrics", url.path)
            self.assertEqual("GET", request.method)
            self.assertTrue("start_date=2022-06-01" in url.query)
            self.assertTrue("end_date=2022-06-30" in url.query)
            self.assertTrue("projects=P1%2CP2" in url.query)
            return response(200, self.va_metrics_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(va_metrics_mock):
            start_date = datetime.datetime(year=2022, month=6, day=1)
            end_date = datetime.datetime(year=2022, month=6, day=30)
            va_metrics_info = self.ams.va_metrics(projects=["P1", "P2"], start_date=start_date, end_date=end_date)
            self.assertEqual(5, va_metrics_info["total_users_count"])
            self.assertEqual(2, va_metrics_info["total_topics_count"])
            self.assertEqual(2, va_metrics_info["total_subscriptions_count"])
            self.assertEqual(16002385, va_metrics_info["projects_metrics"]["total_message_count"])
            self.assertEqual(533412.84, va_metrics_info["projects_metrics"]["average_daily_messages"])
            self.assertEqual("P1", va_metrics_info["projects_metrics"]["projects"][0]["project"])
            self.assertEqual(432148, va_metrics_info["projects_metrics"]["projects"][0]["message_count"])
            self.assertEqual(14404.94, va_metrics_info["projects_metrics"]["projects"][0]["average_daily_messages"])
            self.assertEqual(1, va_metrics_info["projects_metrics"]["projects"][0]["topics_count"])
            self.assertEqual(1, va_metrics_info["projects_metrics"]["projects"][0]["subscriptions_count"])
            self.assertEqual(2, va_metrics_info["projects_metrics"]["projects"][0]["users_count"])
            self.assertEqual("P2", va_metrics_info["projects_metrics"]["projects"][1]["project"])
            self.assertEqual(15570237, va_metrics_info["projects_metrics"]["projects"][1]["message_count"])
            self.assertEqual(519007.9, va_metrics_info["projects_metrics"]["projects"][1]["average_daily_messages"])
            self.assertEqual(1, va_metrics_info["projects_metrics"]["projects"][1]["topics_count"])
            self.assertEqual(1, va_metrics_info["projects_metrics"]["projects"][1]["subscriptions_count"])
            self.assertEqual(3, va_metrics_info["projects_metrics"]["projects"][1]["users_count"])


if __name__ == '__main__':
    unittest.main()
