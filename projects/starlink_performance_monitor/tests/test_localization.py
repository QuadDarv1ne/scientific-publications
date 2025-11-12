import unittest
from src.web.web_app import app, LANGUAGES


CRITICAL_KEYS = [
    # Common UI
    'site_name', 'dashboard', 'settings', 'logout', 'close',
    # Map
    'satellite_map', 'map_layers', 'street_view', 'satellite_view', 'terrain_view',
    'satellite_positions', 'satellite_details', 'loading_satellite_data',
    'initialized_success', 'data_loaded_success', 'error_loading_satellite_data',
    'active_satellite', 'inactive_satellite', 'moving_satellite', 'legend',
    # Settings extras
    'timezone_utc', 'timezone_eastern', 'timezone_london', 'timezone_tokyo', 'timezone_moscow',
    'sqlite_embedded', 'postgresql', 'mysql', 'placeholder_bot_token', 'placeholder_chat_id',
    'smtp_placeholder', 'email_placeholder',
]


class TestLocalization(unittest.TestCase):
    def test_translations_have_critical_keys(self):
        for lang in ["en", "ru"]:
            with self.subTest(lang=lang):
                self.assertIn(lang, LANGUAGES, f"Language {lang} missing in LANGUAGES")
                t = LANGUAGES[lang]
                missing = [k for k in CRITICAL_KEYS if k not in t]
                self.assertFalse(missing, f"Missing keys for {lang}: {missing}")

    def test_pages_render_in_en_and_ru(self):
        cases = [
            ("en", "/", b"Dashboard"),
            ("ru", "/", "Панель управления".encode("utf-8")),
            ("en", "/map", b"Satellite Map"),
            ("ru", "/map", "Карта спутников".encode("utf-8")),
            ("en", "/settings", b"Settings"),
            ("ru", "/settings", "Настройки".encode("utf-8")),
            ("en", "/performance", b"Performance"),
            ("ru", "/performance", "Производительность".encode("utf-8")),
        ]
        app.config.update(TESTING=True)
        for lang, endpoint, expected_text in cases:
            with self.subTest(lang=lang, endpoint=endpoint):
                with app.test_client() as client:
                    with client.session_transaction() as sess:
                        sess['authenticated'] = True
                        sess['username'] = 'tester'
                        sess['language'] = lang
                    resp = client.get(endpoint, follow_redirects=True)
                    self.assertEqual(resp.status_code, 200)
                    self.assertIn(expected_text, resp.data)

    def test_set_language_route_sets_session(self):
        app.config.update(TESTING=True)
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['username'] = 'tester'

            resp = client.get('/set_language/ru', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            with client.session_transaction() as sess:
                self.assertEqual(sess.get('language'), 'ru')

            resp = client.get('/set_language/en', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            with client.session_transaction() as sess:
                self.assertEqual(sess.get('language'), 'en')


if __name__ == '__main__':
    unittest.main()
