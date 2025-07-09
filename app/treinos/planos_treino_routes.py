from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from app.extensions.db import get_db
from app.utils.jwt import extrair_user_info
from app.utils.logs import registrar_log_envio


from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from app.extensions.mail import mail
from flask_mail import Message

import json
import os, requests

planos_treino_bp = Blueprint("planos_treino", __name__, url_prefix="/planos-treino")


# Criar plano de treino (apenas personal)
@planos_treino_bp.route("/", methods=["POST"])
@jwt_required()
@cross_origin()
def criar_plano_treino():
    user = extrair_user_info()
    if user.get("tipo") != "personal":
        return jsonify({"erro": "Apenas personal pode criar planos de treino"}), 403

    dados = request.get_json()
    id_aluno = dados.get("id_aluno")
    nome = dados.get("nome")

    if not id_aluno or not nome:
        return jsonify({"erro": "Campos obrigatórios: id_aluno e nome"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO planos_treino (id_aluno, id_profissional, nome) VALUES (%s, %s, %s)",
        (id_aluno, user["id"], nome),
    )
    conn.commit()
    return jsonify({"mensagem": "Plano criado com sucesso", "id_plano": cursor.lastrowid}), 201


# Listar planos de treino (personal vê os seus, aluno vê os seus)
@planos_treino_bp.route("/", methods=["GET"])
@jwt_required()
@cross_origin()
def listar_planos():
    user = extrair_user_info()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if user["tipo"] == "personal":
        cursor.execute("""
            SELECT p.*, u.nome AS nome_aluno
            FROM planos_treino p
            JOIN usuarios u ON p.id_aluno = u.id_usuario
            WHERE p.id_profissional = %s
        """, (user["id"],))
    elif user["tipo"] == "aluno":
        cursor.execute("""
            SELECT p.*, u.nome AS nome_profissional
            FROM planos_treino p
            JOIN usuarios u ON p.id_profissional = u.id_usuario
            WHERE p.id_aluno = %s
        """, (user["id"],))
    else:
        return jsonify({"erro": "Acesso negado"}), 403

    return jsonify(cursor.fetchall()), 200


# Obter detalhes de um plano específico
@planos_treino_bp.route("/<int:id_plano>", methods=["GET"])
@jwt_required()
@cross_origin()
def obter_plano(id_plano):
    user = extrair_user_info()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if user["tipo"] == "personal":
        cursor.execute("SELECT * FROM planos_treino WHERE id_plano = %s AND id_profissional = %s", (id_plano, user["id"]))
    elif user["tipo"] == "aluno":
        cursor.execute("SELECT * FROM planos_treino WHERE id_plano = %s AND id_aluno = %s", (id_plano, user["id"]))
    else:
        return jsonify({"erro": "Acesso negado"}), 403

    plano = cursor.fetchone()
    if not plano:
        return jsonify({"erro": "Plano não encontrado"}), 404

    return jsonify(plano), 200


# Atualizar nome de um plano (somente personal)
@planos_treino_bp.route("/<int:id_plano>", methods=["PUT"])
@jwt_required()
@cross_origin()
def editar_plano(id_plano):
    user = extrair_user_info()
    if user["tipo"] != "personal":
        return jsonify({"erro": "Apenas personal pode editar planos"}), 403

    dados = request.get_json()
    nome = dados.get("nome")
    if not nome:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE planos_treino SET nome = %s WHERE id_plano = %s AND id_profissional = %s",
        (nome, id_plano, user["id"])
    )
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({"erro": "Plano não encontrado ou não autorizado"}), 404

    return jsonify({"mensagem": "Plano atualizado com sucesso"}), 200


# Deletar plano (somente personal)
@planos_treino_bp.route("/<int:id_plano>", methods=["DELETE"])
@jwt_required()
@cross_origin()
def deletar_plano(id_plano):
    user = extrair_user_info()
    if user["tipo"] != "personal":
        return jsonify({"erro": "Apenas personal pode deletar planos"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM planos_treino WHERE id_plano = %s AND id_profissional = %s",
        (id_plano, user["id"])
    )
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({"erro": "Plano não encontrado ou não autorizado"}), 404

    return jsonify({"mensagem": "Plano deletado com sucesso"}), 200

#============================================================
# Obter detalhes completos de um plano: treinos e exercícios
#============================================================
@planos_treino_bp.route("/<int:id_plano>/detalhes", methods=["GET"])
@jwt_required()
@cross_origin()
def detalhes_plano_treino(id_plano):
    user = extrair_user_info()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Verificar acesso ao plano
    if user["tipo"] == "personal":
        cursor.execute("SELECT * FROM planos_treino WHERE id_plano = %s AND id_profissional = %s", (id_plano, user["id"]))
    elif user["tipo"] == "aluno":
        cursor.execute("SELECT * FROM planos_treino WHERE id_plano = %s AND id_aluno = %s", (id_plano, user["id"]))
    else:
        return jsonify({"erro": "Acesso negado"}), 403

    plano = cursor.fetchone()
    if not plano:
        return jsonify({"erro": "Plano não encontrado ou acesso não autorizado"}), 404

    # Buscar treinos do plano
    cursor.execute("""
        SELECT * FROM treinos
        WHERE id_plano = %s AND ativo = 1
    """, (id_plano,))
    treinos = cursor.fetchall()

    # Para cada treino, buscar exercícios
    for treino in treinos:
        cursor.execute("""
            SELECT te.*, e.nome, e.grupo_muscular
            FROM treinoexercicios te
            JOIN exercicios e ON te.id_exercicio = e.id_exercicio
            WHERE te.id_treino = %s
        """, (treino["id_treino"],))
        treino["exercicios"] = cursor.fetchall()

    plano["treinos"] = treinos
    return jsonify(plano), 200

#==================================
#Buscar dados completo do plano
#==================================
def buscar_dados_plano_completo(id_plano):
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        # Buscar plano + aluno + profissional
        cursor.execute("""
            SELECT p.*, 
                   aluno.nome AS nome_aluno, aluno.email AS email_aluno, aluno.whatsapp,
                   prof.nome AS nome_profissional, prof.telefone, prof.email
            FROM planos_treino p
            JOIN usuarios aluno ON p.id_aluno = aluno.id_usuario
            JOIN usuarios prof ON p.id_profissional = prof.id_usuario
            WHERE p.id_plano = %s
        """, (id_plano,))
        plano = cursor.fetchone()
        if not plano:
            return None

        # Buscar treinos do plano
        cursor.execute("""
            SELECT * FROM treinos WHERE id_plano = %s AND ativo = 1
        """, (id_plano,))
        treinos = cursor.fetchall()

        # Para cada treino, buscar exercícios
        for treino in treinos:
            cursor.execute("""
                SELECT e.nome, e.grupo_muscular, te.series, te.repeticoes, te.observacoes
                FROM treinoexercicios te
                JOIN exercicios e ON te.id_exercicio = e.id_exercicio
                WHERE te.id_treino = %s
            """, (treino["id_treino"],))
            treino["exercicios"] = cursor.fetchall()

        plano["treinos"] = treinos
        return plano

#==================================
#Gerar plano PDF
#==================================
def gerar_pdf_plano_treino(plano, nome_arquivo="plano_treino.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marca d'água com logo
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        marca = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))
        c.drawImage(marca, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()
    except:
        pass

    # Logo no topo
    try:
        c.drawImage(logo_path, 40, height - 80, width=60, height=60, mask='auto')
    except:
        pass

    # Cabeçalho
    c.setFont("Helvetica", 10)
    x = 120
    y = height - 50
    c.drawString(x, y, f"Profissional: {plano.get('nome_profissional')}")
    y -= 15
    c.drawString(x, y, f"Telefone: {plano.get('telefone') or '-'}")
    y -= 15
    c.drawString(x, y, f"E-mail: {plano.get('email') or '-'}")

    c.setLineWidth(1)
    linha_y = y - 10
    c.line(40, linha_y, width - 40, linha_y)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, linha_y - 30, "Plano de Treino")

    # Dados do aluno
    y = linha_y - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, f"Aluno: {plano.get('nome_aluno')}")
    y -= 20
    c.drawString(80, y, f"Plano: {plano.get('nome')}")
    y -= 20

    # Lista de treinos
    for treino in plano.get("treinos", []):
        if y < 150:
            c.showPage()
            y = height - 80

        c.setFont("Helvetica-Bold", 11)
        c.drawString(80, y, f"Treino: {treino.get('nome_treino')}")
        y -= 15

        for ex in treino.get("exercicios", []):
            if y < 100:
                c.showPage()
                y = height - 80
            c.setFont("Helvetica-Bold", 10)
            c.drawString(90, y, f"{ex['nome']} ({ex['grupo_muscular']})")
            y -= 13
            c.setFont("Helvetica", 10)
            c.drawString(
                100, y,
                f"- Séries: {ex['series']}  |  Repetições: {ex['repeticoes']}  |  Obs: {ex.get('observacoes') or '-'}"
            )
            y -= 20

    c.save()
    buffer.seek(0)

    if salvar_em_disco:
        caminho = os.path.join("app", "static", "pdfs", nome_arquivo)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "wb") as f:
            f.write(buffer.getbuffer())
        return caminho
    else:
        return buffer

#==================================
#Download PDF
#==================================
@planos_treino_bp.route("/<int:id_plano>/pdf", methods=["GET"])
@jwt_required()
@cross_origin()
def baixar_pdf_plano(id_plano):
    user = extrair_user_info()
    plano = buscar_dados_plano_completo(id_plano)

    if not plano:
        return jsonify({"erro": "Plano não encontrado"}), 404

    # Garantir que apenas o aluno dono ou o personal dono veja
    if user["tipo"] == "personal" and plano["id_profissional"] != user["id"]:
        return jsonify({"erro": "Acesso negado"}), 403
    if user["tipo"] == "aluno" and plano["id_aluno"] != user["id"]:
        return jsonify({"erro": "Acesso negado"}), 403

    try:
        pdf = gerar_pdf_plano_treino(plano)
        return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name="plano_treino.pdf")
    except Exception as e:
        print(f"[ERRO PDF] {e}")
        return jsonify({"erro": "Erro ao gerar PDF"}), 500
    

#===========================
#Função enviar por e-mail
#===========================
@planos_treino_bp.route("/<int:id_plano>/enviar", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_plano_treino(id_plano):
    try:
        user = extrair_user_info()
        plano = buscar_dados_plano_completo(id_plano)
        if not plano:
            return jsonify({"message": "Plano não encontrado"}), 404

        # Verificar permissão de acesso
        if user["tipo"] == "personal" and plano["id_profissional"] != user["id"]:
            return jsonify({"erro": "Acesso negado"}), 403
        if user["tipo"] == "aluno" and plano["id_aluno"] != user["id"]:
            return jsonify({"erro": "Acesso negado"}), 403

        email = plano.get("email_aluno")
        nome = plano.get("nome_aluno") or "Aluno"

        if not email:
            return jsonify({"message": "E-mail do aluno não encontrado"}), 403

        try:
            pdf_stream = gerar_pdf_plano_treino(plano)  # retorna BytesIO
        except Exception as e:
            print("Erro ao gerar PDF do plano:", e)
            registrar_log_envio(plano["id_aluno"], "email", email, "Erro ao gerar PDF do plano", "falha")
            return jsonify({"message": "Erro ao gerar o plano em PDF"}), 500

        try:
            msg = Message(
                subject="Seu Plano de Treino - Alpphas GYM",
                sender=None,
                recipients=[email],
                body=(
                    f"Olá {nome},\n\n"
                    f"Segue em anexo seu plano de treino personalizado.\n\n"
                    f"Atenciosamente,\nEquipe Alpphas GYM"
                )
            )
            msg.attach(
                filename=f"plano_treino_{id_plano}.pdf",
                content_type="application/pdf",
                data=pdf_stream.getvalue()
            )
            mail.send(msg)

            registrar_log_envio(plano["id_aluno"], "email", email, "Envio de plano de treino em PDF", "sucesso")
            return jsonify({"message": "Plano enviado com sucesso por e-mail."}), 200

        except Exception as e:
            print("Erro ao enviar e-mail com plano:", e)
            registrar_log_envio(plano["id_aluno"], "email", email, "Erro ao enviar plano", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar o e-mail: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado ao enviar plano:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio do plano."}), 500
    

#============================
#Função enviar via WhatsApp
#============================
@planos_treino_bp.route("/<int:id_plano>/enviar-whatsapp", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_plano_whatsapp(id_plano):
    try:
        user = extrair_user_info()
        plano = buscar_dados_plano_completo(id_plano)
        if not plano:
            return jsonify({"message": "Plano não encontrado"}), 404

        # Verificar permissão
        if user["tipo"] == "personal" and plano["id_profissional"] != user["id"]:
            return jsonify({"erro": "Acesso negado"}), 403
        if user["tipo"] == "aluno" and plano["id_aluno"] != user["id"]:
            return jsonify({"erro": "Acesso negado"}), 403

        numero = plano.get("whatsapp")
        nome = plano.get("nome_aluno", "Aluno")

        if not numero:
            return jsonify({"message": "WhatsApp do aluno não encontrado"}), 403

        # Gerar PDF e salvar em disco
        try:
            nome_arquivo = f"plano_treino_{id_plano}.pdf"
            gerar_pdf_plano_treino(plano, nome_arquivo=nome_arquivo, salvar_em_disco=True)
        except Exception as e:
            print("Erro ao gerar PDF do plano:", e)
            registrar_log_envio(plano["id_aluno"], "whatsapp", numero, "Erro ao gerar PDF do plano", "falha")
            return jsonify({"message": "Erro ao gerar o PDF do plano"}), 500

        # Montar link público
        url_base = os.getenv("APP_URL", "http://localhost:5000")
        url_pdf = f"{url_base}/planos-treino/{id_plano}/pdf"

        mensagem = (
            f"Olá {nome}, segue o link para seu plano de treino personalizado:\n\n{url_pdf}\n\n"
            f"Atenciosamente,\nEquipe Alpphas GYM"
        )

        instancia = os.getenv("ULTRAMSG_INSTANCE")
        token = os.getenv("ULTRAMSG_TOKEN")
        payload = {
            "token": token,
            "to": numero,
            "body": mensagem
        }

        try:
            response = requests.post(
                f"https://api.ultramsg.com/{instancia}/messages/chat",
                json=payload
            )
            response.raise_for_status()

            registrar_log_envio(plano["id_aluno"], "whatsapp", numero, mensagem, "sucesso")
            return jsonify({"message": "Plano enviado com sucesso via WhatsApp"}), 200

        except Exception as e:
            print("Erro ao enviar WhatsApp do plano:", e)
            registrar_log_envio(plano["id_aluno"], "whatsapp", numero, f"Erro no envio WhatsApp: {mensagem}", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar via WhatsApp: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado no envio:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio do plano via WhatsApp."}), 500
    