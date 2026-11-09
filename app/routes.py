from datetime import date
import sqlite3

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


@main.get("/frequencias")
def attendance():
    database = get_db()
    participants = database.execute(
        "SELECT id_participante, nome FROM participantes ORDER BY nome COLLATE NOCASE"
    ).fetchall()
    workshops = database.execute(
        "SELECT id_oficina, nome_oficina FROM oficinas "
        "ORDER BY nome_oficina COLLATE NOCASE"
    ).fetchall()
    records = database.execute(
        """
        SELECT frequencias.data_presenca, frequencias.presente,
               participantes.nome, oficinas.nome_oficina
        FROM frequencias
        JOIN participantes
            ON participantes.id_participante = frequencias.id_participante
        JOIN oficinas ON oficinas.id_oficina = frequencias.id_oficina
        ORDER BY frequencias.data_presenca DESC, participantes.nome COLLATE NOCASE
        """
    ).fetchall()
    return render_template(
        "attendance.html",
        participants=participants,
        workshops=workshops,
        records=records,
    )


@main.post("/frequencias")
def create_attendance():
    participant_id = request.form.get("id_participante", "").strip()
    workshop_id = request.form.get("id_oficina", "").strip()
    attendance_date = request.form.get("data_presenca", "").strip()
    present_value = request.form.get("presente", "")

    if not participant_id or not workshop_id or not attendance_date:
        flash("Selecione o participante, a oficina e a data da frequência.", "error")
        return redirect(url_for("main.attendance"))

    try:
        participant_id_number = int(participant_id)
        workshop_id_number = int(workshop_id)
        parsed_date = date.fromisoformat(attendance_date)
    except ValueError:
        flash("Informe participante, oficina e data válidos.", "error")
        return redirect(url_for("main.attendance"))

    if (
        participant_id != str(participant_id_number)
        or workshop_id != str(workshop_id_number)
        or attendance_date != parsed_date.isoformat()
    ):
        flash("Informe participante, oficina e data válidos.", "error")
        return redirect(url_for("main.attendance"))

    if present_value not in {"0", "1"}:
        flash("Selecione se o participante esteve presente ou ausente.", "error")
        return redirect(url_for("main.attendance"))

    database = get_db()
    participant = database.execute(
        "SELECT 1 FROM participantes WHERE id_participante = ?",
        (participant_id_number,),
    ).fetchone()
    workshop = database.execute(
        "SELECT 1 FROM oficinas WHERE id_oficina = ?",
        (workshop_id_number,),
    ).fetchone()
    if participant is None or workshop is None:
        flash("O participante ou a oficina selecionada não foi encontrado.", "error")
        return redirect(url_for("main.attendance"))

    try:
        database.execute(
            """
            INSERT INTO frequencias
                (id_participante, id_oficina, data_presenca, presente)
            VALUES (?, ?, ?, ?)
            """,
            (
                participant_id_number,
                workshop_id_number,
                attendance_date,
                int(present_value),
            ),
        )
        database.commit()
    except sqlite3.IntegrityError:
        database.rollback()
        flash(
            "Já existe uma frequência registrada para esse participante, oficina e data.",
            "error",
        )
        return redirect(url_for("main.attendance"))

    flash("Frequência registrada com sucesso.", "success")
    return redirect(url_for("main.attendance"))
