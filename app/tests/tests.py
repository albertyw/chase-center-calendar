import unittest

from varsnap import test

from app import cache, serve


def setUpModule() -> None:
    cache.get_cache_file(cache.CACHED_CHASECENTER).unlink(missing_ok=True)
    cache.get_cache_file(cache.CACHED_ORACLEPARK).unlink(missing_ok=True)
    cache.get_cache_file(cache.CACHED_CHASECENTER_ICS).unlink(missing_ok=True)
    cache.get_cache_file(cache.CACHED_ORACLEPARK_ICS).unlink(missing_ok=True)


class PageCase(unittest.TestCase):
    def setUp(self) -> None:
        serve.app.config['TESTING'] = True
        self.app = serve.app.test_client()

    def test_index_load(self) -> None:
        self.page_test('/', b'Chase Center Calendar')

    def test_robots_load(self) -> None:
        self.page_test('/robots.txt', b'')

    def test_security_load(self) -> None:
        self.page_test('/.well-known/security.txt', b'Contact')

    def test_humans_load(self) -> None:
        self.page_test('/humans.txt', b'albertyw')

    def test_health_load(self) -> None:
        self.page_test('/health', b'ok')

    def test_sitemap_load(self) -> None:
        self.page_test('/sitemap.xml', b'')

    def test_not_found(self) -> None:
        response = self.app.get('/asdf')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Not Found', response.get_data())

    def test_about(self) -> None:
        self.page_test('/about', b'Chase Center Calendar')

    def test_chase_center(self) -> None:
        self.page_test('/chase_center', b'Chase Center Calendar')

    def test_ical_file(self) -> None:
        self.page_test('/chasecenter.ics', b'BEGIN:VCALENDAR')

    def test_ical_view(self) -> None:
        self.page_test('/ical_view', b'.ics')

    def test_oracle_park(self) -> None:
        self.page_test('/oracle_park', b'Oracle Park Calendar')

    def test_oracle_park_ical_file(self) -> None:
        self.page_test('/oraclepark.ics', b'BEGIN:VCALENDAR')

    def page_test(self, path: str, string: bytes) -> None:
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertIn(string, response.get_data())
        response.close()


class TestIntegration(unittest.TestCase):
    def test_varsnap(self) -> None:
        with serve.app.test_request_context():
            matches, logs = test()
        if matches is None:
            raise unittest.case.SkipTest('No Snaps found')  # pragma: no cover
        self.assertTrue(matches, logs)
