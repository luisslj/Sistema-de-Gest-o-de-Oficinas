from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app


class ReportsTests(unittest.TestCase):
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
        with closing(sqlite3.connect(database_path)) as database:
            database.executemany(
                "INSERT INTO participantes (nome) VALUES (?)",
                [("Ana Silva",), ("Bruno Lima",)],
            )
            database.executemany(
                """
                INSERT INTO oficinas (nome_oficina, descricao, data_inicio)
                VALUES (?, ?, ?)
                """,
                [
                    ("Artesanato", "Oficina de artesanato.", "2026-03-01"),
                    ("Pintura", "Oficina de pintura.", "2026-03-01"),
                ],
            )
            database.executemany(
                """
                INSERT INTO frequencias
                    (id_participante, id_oficina, data_presenca, presente)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (1, 1, "2026-03-10", 1),
                    (1, 2, "2026-03-11", 0),
                    (2, 1, "2026-03-12", 1),
                ],
            )
            database.commit()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_reports_all_attendance_and_summary(self) -> None:
        response = self.client.get("/relatorios")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ana Silva", response.data)
        self.assertIn(b"Bruno Lima", response.data)
        self.assertIn(b"Artesanato", response.data)
        self.assertIn(b"Pintura", response.data)
        self.assertIn(b"Total de registros: 3", response.data)
        self.assertIn(b"Presen\xc3\xa7as: 2", response.data)
        self.assertIn(b"Aus\xc3\xaancias: 1", response.data)

    def test_filters_attendance_by_participant_and_workshop(self) -> None:
        response = self.client.get("/relatorios?id_participante=1&id_oficina=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ana Silva", response.data)
        self.assertIn(b"Pintura", response.data)
        self.assertIn(b"Total de registros: 1", response.data)
        self.assertIn(b"Presen\xc3\xa7as: 0", response.data)
        self.assertIn(b"Aus\xc3\xaancias: 1", response.data)
        results_table = (
            response.get_data(as_text=True).split("<tbody>", 1)[1].split("</tbody>", 1)[0]
        )
        self.assertNotIn("Bruno Lima", results_table)

    def test_invalid_filter_returns_empty_report(self) -> None:
        response = self.client.get("/relatorios?id_participante=invalid")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nenhuma frequ", response.data)
        self.assertIn(b"Total de registros: 0", response.data)


if __name__ == "__main__":
    unittest.main()
