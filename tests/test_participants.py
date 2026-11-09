from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app


class ParticipantRegistrationTests(unittest.TestCase):
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

    def test_registers_and_lists_participant(self) -> None:
        response = self.client.post(
            "/participantes",
            data={
                "nome": "Ana da Silva",
                "telefone": "(11) 99999-0000",
                "data_nascimento": "2000-01-15",
                "endereco": "Rua das Flores, 10",
                "status": "ativo",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ana da Silva", response.data)
        self.assertIn(b"Participante cadastrado com sucesso.", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            row = database.execute(
                """
                SELECT nome, telefone, data_nascimento, endereco, status
                FROM participantes
                """
            ).fetchone()
        self.assertEqual(
            row,
            (
                "Ana da Silva",
                "(11) 99999-0000",
                "2000-01-15",
                "Rua das Flores, 10",
                "ativo",
            ),
        )

    def test_rejects_missing_name(self) -> None:
        response = self.client.post(
            "/participantes",
            data={"nome": "  "},
            follow_redirects=True,
        )

        self.assertIn(b"Informe o nome do participante.", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute(
                "SELECT COUNT(*) FROM participantes"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_rejects_fields_over_maximum_length(self) -> None:
        response = self.client.post(
            "/participantes",
            data={"nome": "A" * 201},
            follow_redirects=True,
        )

        self.assertIn(b"limites de tamanho", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute(
                "SELECT COUNT(*) FROM participantes"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_rejects_invalid_date_and_status(self) -> None:
        invalid_date = self.client.post(
            "/participantes",
            data={"nome": "Ana", "data_nascimento": "31-02-2000"},
            follow_redirects=True,
        )
        invalid_status = self.client.post(
            "/participantes",
            data={"nome": "Ana", "status": "desconhecido"},
            follow_redirects=True,
        )

        self.assertIn(b"data de nascimento", invalid_date.data)
        self.assertIn(b"status v", invalid_status.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute(
                "SELECT COUNT(*) FROM participantes"
            ).fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
