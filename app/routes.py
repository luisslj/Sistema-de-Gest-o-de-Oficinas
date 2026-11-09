from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .database import get_db


main = Blueprint("main", __name__)


@main.get("/")
def index():
    return render_template("index.html")


@main.get("/participantes")
def participants():
    rows = get_db().execute(
        "SELECT * FROM participantes ORDER BY nome COLLATE NOCASE"
    ).fetchall()
    return render_template("participants.html", participants=rows)


@main.post("/participantes")
def create_participant():
    nome = request.form.get("nome", "").strip()
    telefone = request.form.get("telefone", "").strip()
    data_nascimento = request.form.get("data_nascimento", "").strip()
    endereco = request.form.get("endereco", "").strip()
    status = request.form.get("status", "ativo")

    if not nome:
        flash("Informe o nome do participante.", "error")
        return redirect(url_for("main.participants"))

    if len(nome) > 200 or len(telefone) > 30 or len(endereco) > 300:
        flash("Revise os limites de tamanho dos campos informados.", "error")
        return redirect(url_for("main.participants"))

    if data_nascimento:
        try:
            date.fromisoformat(data_nascimento)
        except ValueError:
            flash("Informe uma data de nascimento válida.", "error")
            return redirect(url_for("main.participants"))

    if status not in {"ativo", "inativo"}:
        flash("Selecione um status válido.", "error")
        return redirect(url_for("main.participants"))

    database = get_db()
    database.execute(
        """
        INSERT INTO participantes (nome, telefone, data_nascimento, endereco, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            nome,
            telefone or None,
            data_nascimento or None,
            endereco or None,
            status,
        ),
    )
    database.commit()
    flash("Participante cadastrado com sucesso.", "success")
    return redirect(url_for("main.participants"))
