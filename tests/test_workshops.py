from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app


class WorkshopRegistrationTests(unittest.TestCase):
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

    def test_registers_and_lists_workshop(self) -> None:
        response = self.client.post(
            "/oficinas",
            data={
                "nome_oficina": "Artesanato",
                "descricao": "Oficina de artesanato para a comunidade.",
                "data_inicio": "2026-03-01",
                "data_fim": "2026-06-30",
                "status": "ativa",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Artesanato", response.data)
        self.assertIn(b"Oficina cadastrada com sucesso.", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            row = database.execute(
                """
                SELECT nome_oficina, descricao, data_inicio, data_fim, status
                FROM oficinas
                """
            ).fetchone()
        self.assertEqual(
            row,
            (
                "Artesanato",
                "Oficina de artesanato para a comunidade.",
                "2026-03-01",
                "2026-06-30",
                "ativa",
            ),
        )

    def test_rejects_missing_required_fields(self) -> None:
        response = self.client.post(
            "/oficinas",
            data={"nome_oficina": "Artesanato"},
            follow_redirects=True,
        )

        self.assertIn(b"Preencha o nome", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute("SELECT COUNT(*) FROM oficinas").fetchone()[0]
        self.assertEqual(count, 0)

    def test_rejects_invalid_dates_and_status(self) -> None:
        invalid_date = self.client.post(
            "/oficinas",
            data={
                "nome_oficina": "Artesanato",
                "descricao": "Oficina comunitária.",
                "data_inicio": "31-02-2026",
            },
            follow_redirects=True,
        )
        invalid_period = self.client.post(
            "/oficinas",
            data={
                "nome_oficina": "Artesanato",
                "descricao": "Oficina comunitária.",
                "data_inicio": "2026-06-30",
                "data_fim": "2026-03-01",
            },
            follow_redirects=True,
        )
        invalid_status = self.client.post(
            "/oficinas",
            data={
                "nome_oficina": "Artesanato",
                "descricao": "Oficina comunitária.",
                "data_inicio": "2026-03-01",
                "status": "desconhecido",
            },
            follow_redirects=True,
        )

        self.assertIn(b"datas v", invalid_date.data)
        self.assertIn(b"anterior", invalid_period.data)
        self.assertIn(b"status v", invalid_status.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute("SELECT COUNT(*) FROM oficinas").fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
