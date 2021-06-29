import unittest

from varsnap import test

from app import serve


class PageCase(unittest.TestCase):
    def setUp(self) -> None:
        serve.app.config['TESTING'] = True
        self.app = serve.app.test_client()

    def test_index_load(self) -> None:
        self.page_test('/', b'')

    def test_robots_load(self) -> None:
        self.page_test('/robots.txt', b'')

    def test_health_load(self) -> None:
        self.page_test('/health', b'ok')

    def test_sitemap_load(self) -> None:
        self.page_test('/sitemap.xml', b'')

    def test_not_found(self) -> None:
        response = self.app.get('/asdf')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Not Found', response.get_data())

    def test_about(self) -> None:
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chase Center Calendar', response.get_data())

    def test_ical_view(self) -> None:
        response = self.app.get('/ical_view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BEGIN:VCALENDAR', response.get_data())

    def page_test(self, path: str, string: bytes) -> None:
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertIn(string, response.get_data())


class TestIntegration(unittest.TestCase):
    def test_varsnap(self) -> None:
        with serve.app.test_request_context():
            matches, logs = test()
        if matches is None:
            raise unittest.case.SkipTest('No Snaps found')  # pragma: no cover
        self.assertTrue(matches, logs)
