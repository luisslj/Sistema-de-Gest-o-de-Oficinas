import tempfile
import unittest
from pathlib import Path

from app import create_app


class AccessibilityAndResponsiveLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(database_path),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_all_pages_share_accessible_navigation_and_mobile_styles(self) -> None:
        paths = (
            "/",
            "/participantes",
            "/oficinas",
            "/frequencias",
            "/relatorios",
        )
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'name="viewport"', response.data)
                self.assertIn(b'href="#conteudo"', response.data)
                self.assertIn(
                    b'aria-label="Navega\xc3\xa7\xc3\xa3o principal"',
                    response.data,
                )
                self.assertIn(b"/static/styles.css", response.data)

        styles = self.client.get("/static/styles.css")
        self.assertEqual(styles.status_code, 200)
        self.assertIn(b"@media (max-width: 48rem)", styles.data)
        self.assertIn(b":focus-visible", styles.data)
        self.assertIn(b"min-height: 48px", styles.data)
        self.assertIn(b"prefers-reduced-motion", styles.data)
        styles.close()


if __name__ == "__main__":
    unittest.main()
