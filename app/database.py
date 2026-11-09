import sqlite3
from pathlib import Path

import click
from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db() -> None:
    database = get_db()
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS participantes (
            id_participante INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            data_nascimento TEXT,
            endereco TEXT,
            status TEXT NOT NULL DEFAULT 'ativo'
                CHECK (status IN ('ativo', 'inativo'))
        )
        """
    )
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS oficinas (
            id_oficina INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_oficina TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT,
            status TEXT NOT NULL DEFAULT 'ativa'
                CHECK (status IN ('ativa', 'inativa'))
        )
        """
    )
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS frequencias (
            id_frequencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_participante INTEGER NOT NULL,
            id_oficina INTEGER NOT NULL,
            data_presenca TEXT NOT NULL,
            presente INTEGER NOT NULL CHECK (presente IN (0, 1)),
            FOREIGN KEY (id_participante)
                REFERENCES participantes (id_participante),
            FOREIGN KEY (id_oficina)
                REFERENCES oficinas (id_oficina),
            UNIQUE (id_participante, id_oficina, data_presenca)
        )
        """
    )
    database.commit()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.cli.command("init-db")
    def init_db_command() -> None:
        init_db()
        click.echo("Banco de dados inicializado.")
