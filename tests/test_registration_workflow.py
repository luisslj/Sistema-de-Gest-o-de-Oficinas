from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app


class RegistrationWorkflowTests(unittest.TestCase):
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

    def test_registers_participant_workshop_and_attendance(self) -> None:
        participant_response = self.client.post(
            "/participantes",
            data={
                "nome": "Mariana Souza",
                "telefone": "(11) 99999-1234",
                "status": "ativo",
            },
            follow_redirects=True,
        )
        workshop_response = self.client.post(
            "/oficinas",
            data={
                "nome_oficina": "Pintura",
                "descricao": "Oficina de pintura comunitária.",
                "data_inicio": "2026-03-01",
                "status": "ativa",
            },
            follow_redirects=True,
        )

        self.assertIn(b"Mariana Souza", participant_response.data)
        self.assertIn(b"Participante cadastrado com sucesso.", participant_response.data)
        self.assertIn(b"Pintura", workshop_response.data)
        self.assertIn(b"Oficina cadastrada com sucesso.", workshop_response.data)

        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            participant_id = database.execute(
                "SELECT id_participante FROM participantes WHERE nome = ?",
                ("Mariana Souza",),
            ).fetchone()[0]
            workshop_id = database.execute(
                "SELECT id_oficina FROM oficinas WHERE nome_oficina = ?",
                ("Pintura",),
            ).fetchone()[0]

        attendance_response = self.client.post(
            "/frequencias",
            data={
                "id_participante": str(participant_id),
                "id_oficina": str(workshop_id),
                "data_presenca": "2026-03-10",
                "presente": "1",
            },
            follow_redirects=True,
        )

        self.assertIn(b"Frequ", attendance_response.data)
        self.assertIn(b"Mariana Souza", attendance_response.data)
        self.assertIn(b"Pintura", attendance_response.data)
        self.assertIn(b"Presente", attendance_response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            attendance = database.execute(
                """
                SELECT id_participante, id_oficina, data_presenca, presente
                FROM frequencias
                """
            ).fetchone()
        self.assertEqual(
            attendance,
            (participant_id, workshop_id, "2026-03-10", 1),
        )


if __name__ == "__main__":
    unittest.main()
