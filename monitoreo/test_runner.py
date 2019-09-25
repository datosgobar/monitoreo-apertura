import requests_mock
from django_nose import NoseTestSuiteRunner


class MonitoreoTestRunner(NoseTestSuiteRunner):

    def setup_test_environment(self, **kwargs):
        super(MonitoreoTestRunner, self).setup_test_environment(**kwargs)
        self.mocker = requests_mock.Mocker()
        self.mocker.head(requests_mock.ANY, status_code=200)
        self.mocker.start()

    def teardown_test_environment(self, **kwargs):
        super(MonitoreoTestRunner, self).teardown_test_environment(**kwargs)
        self.mocker.stop()
