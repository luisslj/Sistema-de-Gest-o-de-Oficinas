from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app


class AttendanceRegistrationTests(unittest.TestCase):
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
            database.execute(
                "INSERT INTO participantes (nome) VALUES (?)",
                ("Ana da Silva",),
            )
            database.execute(
                """
                INSERT INTO oficinas (nome_oficina, descricao, data_inicio)
                VALUES (?, ?, ?)
                """,
                ("Artesanato", "Oficina comunitária.", "2026-03-01"),
            )
            database.commit()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_registers_and_lists_attendance(self) -> None:
        response = self.client.post(
            "/frequencias",
            data={
                "id_participante": "1",
                "id_oficina": "1",
                "data_presenca": "2026-03-10",
                "presente": "1",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"registrada com sucesso.", response.data)
        self.assertIn(b"Ana da Silva", response.data)
        self.assertIn(b"Artesanato", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            row = database.execute(
                """
                SELECT id_participante, id_oficina, data_presenca, presente
                FROM frequencias
                """
            ).fetchone()
        self.assertEqual(row, (1, 1, "2026-03-10", 1))

    def test_registers_absence(self) -> None:
        response = self.client.post(
            "/frequencias",
            data={
                "id_participante": "1",
                "id_oficina": "1",
                "data_presenca": "2026-03-10",
                "presente": "0",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ausente", response.data)

    def test_rejects_missing_or_invalid_fields(self) -> None:
        missing_fields = self.client.post(
            "/frequencias",
            data={"id_participante": "1"},
            follow_redirects=True,
        )
        invalid_record = self.client.post(
            "/frequencias",
            data={
                "id_participante": "999",
                "id_oficina": "1",
                "data_presenca": "2026-03-10",
                "presente": "1",
            },
            follow_redirects=True,
        )
        invalid_presence = self.client.post(
            "/frequencias",
            data={
                "id_participante": "1",
                "id_oficina": "1",
                "data_presenca": "2026-03-10",
                "presente": "yes",
            },
            follow_redirects=True,
        )
        invalid_workshop = self.client.post(
            "/frequencias",
            data={
                "id_participante": "1",
                "id_oficina": "999",
                "data_presenca": "2026-03-10",
                "presente": "1",
            },
            follow_redirects=True,
        )

        self.assertIn(b"Selecione o participante", missing_fields.data)
        self.assertIn(b"foi encontrado.", invalid_record.data)
        self.assertIn(b"esteve presente ou ausente.", invalid_presence.data)
        self.assertIn(b"foi encontrado.", invalid_workshop.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute("SELECT COUNT(*) FROM frequencias").fetchone()[0]
        self.assertEqual(count, 0)

    def test_reports_database_integrity_error_without_claiming_duplicate(self) -> None:
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            database.execute(
                """
                CREATE TRIGGER reject_attendance_insert
                BEFORE INSERT ON frequencias
                BEGIN
                    SELECT RAISE(ABORT, 'forced integrity failure');
                END
                """
            )
            database.commit()

        response = self.client.post(
            "/frequencias",
            data={
                "id_participante": "1",
                "id_oficina": "1",
                "data_presenca": "2026-03-10",
                "presente": "1",
            },
            follow_redirects=True,
        )

        self.assertIn(b"N\xc3\xa3o foi poss\xc3\xadvel gravar a frequ\xc3\xaancia", response.data)
        self.assertNotIn(b"J\xc3\xa1 existe uma frequ\xc3\xaancia", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute("SELECT COUNT(*) FROM frequencias").fetchone()[0]
        self.assertEqual(count, 0)

    def test_prevents_duplicate_attendance_for_same_day(self) -> None:
        form_data = {
            "id_participante": "1",
            "id_oficina": "1",
            "data_presenca": "2026-03-10",
            "presente": "1",
        }
        self.client.post("/frequencias", data=form_data)
        response = self.client.post(
            "/frequencias",
            data=form_data,
            follow_redirects=True,
        )

        self.assertIn(b"existe uma frequ", response.data)
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as database:
            count = database.execute("SELECT COUNT(*) FROM frequencias").fetchone()[0]
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
