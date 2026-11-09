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


@main.get("/oficinas")
def workshops():
    rows = get_db().execute(
        "SELECT * FROM oficinas ORDER BY nome_oficina COLLATE NOCASE"
    ).fetchall()
    return render_template("workshops.html", workshops=rows)


@main.post("/oficinas")
def create_workshop():
    nome_oficina = request.form.get("nome_oficina", "").strip()
    descricao = request.form.get("descricao", "").strip()
    data_inicio = request.form.get("data_inicio", "").strip()
    data_fim = request.form.get("data_fim", "").strip()
    status = request.form.get("status", "ativa")

    if not nome_oficina or not descricao or not data_inicio:
        flash("Preencha o nome, a descrição e a data de início da oficina.", "error")
        return redirect(url_for("main.workshops"))

    if (
        len(nome_oficina) > 200
        or len(descricao) > 2000
        or len(data_inicio) > 10
        or len(data_fim) > 10
    ):
        flash("Revise os limites de tamanho dos campos informados.", "error")
        return redirect(url_for("main.workshops"))

    try:
        inicio = date.fromisoformat(data_inicio)
        fim = date.fromisoformat(data_fim) if data_fim else None
    except ValueError:
        flash("Informe datas válidas para a oficina.", "error")
        return redirect(url_for("main.workshops"))

    if data_inicio != inicio.isoformat() or (
        fim is not None and data_fim != fim.isoformat()
    ):
        flash("Informe as datas no formato válido.", "error")
        return redirect(url_for("main.workshops"))

    if fim is not None and fim < inicio:
        flash("A data de término não pode ser anterior à data de início.", "error")
        return redirect(url_for("main.workshops"))

    if status not in {"ativa", "inativa"}:
        flash("Selecione um status válido para a oficina.", "error")
        return redirect(url_for("main.workshops"))

    database = get_db()
    database.execute(
        """
        INSERT INTO oficinas (nome_oficina, descricao, data_inicio, data_fim, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            nome_oficina,
            descricao,
            data_inicio,
            data_fim or None,
            status,
        ),
    )
    database.commit()
    flash("Oficina cadastrada com sucesso.", "success")
    return redirect(url_for("main.workshops"))
