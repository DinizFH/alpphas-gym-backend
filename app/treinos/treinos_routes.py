from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
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

treinos_bp = Blueprint("treinos", __name__)

def extrair_user_info():
    identidade = get_jwt_identity()
    try:
        return json.loads(identidade) if isinstance(identidade, str) else identidade
    except Exception:
        return {}

# =======================
# Criar novo treino
# =======================
@treinos_bp.route("/", methods=["POST"])
@jwt_required()
def criar_treino():
    identidade = extrair_user_info()
    print("DEBUG - Identidade recebida no treino:", identidade)
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas usuários do tipo 'personal' podem criar treinos"}), 403

    data = request.get_json()
    id_aluno = data.get("id_aluno")
    nome_treino = data.get("nome_treino")
    objetivo = data.get("objetivo", "")
    exercicios = data.get("exercicios", [])

    if not all([id_aluno, nome_treino]) or not exercicios:
        return jsonify({"message": "Campos obrigatórios não fornecidos"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO treinos (id_aluno, id_profissional, nome_treino, objetivo, ativo)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (id_aluno, identidade.get("id"), nome_treino, objetivo))
            id_treino = cursor.lastrowid

            for ex in exercicios:
                cursor.execute("""
                    INSERT INTO treinoexercicios (id_treino, id_exercicio, series, repeticoes, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_treino,
                    ex.get("id_exercicio"),
                    ex.get("series"),
                    ex.get("repeticoes"),
                    ex.get("observacoes")
                ))

            db.commit()
            return jsonify({
                "message": "Treino criado com sucesso",
                "id_treino": id_treino
            }), 201

    except Exception as e:
        print("Erro ao criar treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Listar treinos por profissional
# =======================
@treinos_bp.route("/profissional", methods=["GET"])
@jwt_required()
def listar_treinos_por_profissional():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode acessar"}), 403

    nome = request.args.get("nome", "")
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT u.id_usuario, u.nome, u.cpf,
                       t.id_treino, t.nome_treino, t.data_criacao
                FROM usuarios u
                JOIN treinos t ON u.id_usuario = t.id_aluno
                WHERE t.id_profissional = %s AND t.ativo = TRUE AND u.nome LIKE %s
                ORDER BY u.nome, t.nome_treino
            """, (identidade.get("id"), f"%{nome}%"))
            dados = cursor.fetchall()

            resposta = {}
            for row in dados:
                uid = row["id_usuario"]
                if uid not in resposta:
                    resposta[uid] = {
                        "id_usuario": uid,
                        "nome": row["nome"],
                        "cpf": row["cpf"],
                        "treinos": []
                    }
                resposta[uid]["treinos"].append({
                    "id_treino": row["id_treino"],
                    "nome_treino": row["nome_treino"],
                    "data_criacao": row["data_criacao"]
                })
            return jsonify(list(resposta.values())), 200
    except Exception as e:
        print("Erro ao listar treinos:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Editar treino
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["PUT"])
@jwt_required()
def editar_treino(id_treino):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode editar treinos"}), 403

    data = request.get_json()
    nome_treino = data.get("nome_treino")
    exercicios = data.get("exercicios", [])

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE treinos SET nome_treino = %s WHERE id_treino = %s
            """, (nome_treino, id_treino))

            cursor.execute("DELETE FROM treinoexercicios WHERE id_treino = %s", (id_treino,))
            for ex in exercicios:
                cursor.execute("""
                    INSERT INTO treinoexercicios (id_treino, id_exercicio, series, repeticoes, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_treino, ex["id_exercicio"], ex["series"], ex["repeticoes"], ex["observacoes"]))

            db.commit()
            return jsonify({"message": "Treino atualizado com sucesso"}), 200
    except Exception as e:
        print("Erro ao editar treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Excluir treino (inativar)
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["DELETE"])
@jwt_required()
def excluir_treino(id_treino):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode excluir treinos"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE treinos SET ativo = FALSE WHERE id_treino = %s", (id_treino,))
            db.commit()
            return jsonify({"message": "Treino excluído com sucesso"}), 200
    except Exception as e:
        print("Erro ao excluir treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# ==============================
# Listar treinos do aluno logado
# ==============================
@treinos_bp.route("/aluno", methods=["GET"])
@jwt_required()
def listar_treinos_aluno():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "aluno":
        return jsonify({"message": "Apenas alunos podem acessar esta rota"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_treino, nome_treino
                FROM treinos
                WHERE id_aluno = %s AND ativo = TRUE
                ORDER BY nome_treino
            """, (identidade.get("id"),))
            treinos = cursor.fetchall()
            return jsonify(treinos), 200
    except Exception as e:
        print("Erro ao listar treinos do aluno:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Listar treinos de um aluno por ID (usado por personal)
# =======================
@treinos_bp.route("/aluno/<int:id_aluno>", methods=["GET"])
@jwt_required()
def listar_treinos_de_um_aluno(id_aluno):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode acessar esta rota"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_treino, nome_treino
                FROM treinos
                WHERE id_aluno = %s AND ativo = TRUE
                ORDER BY nome_treino
            """, (id_aluno,))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar treinos do aluno:", e)
        return jsonify({"message": "Erro interno ao listar treinos"}), 500
    finally:
        db.close()

# =======================
# Obter detalhes do treino
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["GET"])
@jwt_required()
def detalhes_treino(id_treino):
    identidade = extrair_user_info()
    tipo = identidade.get("tipo_usuario")
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT t.id_treino, t.nome_treino, t.id_aluno, u.nome AS nome_aluno, u.cpf AS cpf_aluno
                FROM treinos t
                JOIN usuarios u ON u.id_usuario = t.id_aluno
                WHERE t.id_treino = %s AND t.ativo = TRUE
            """, (id_treino,))
            treino = cursor.fetchone()
            if not treino:
                return jsonify({"message": "Treino não encontrado"}), 404

            if tipo == "aluno" and treino["id_aluno"] != identidade.get("id"):
                return jsonify({"message": "Acesso negado"}), 403

            cursor.execute("""
                SELECT e.id_exercicio, e.nome, e.grupo_muscular, e.video,
                       te.series, te.repeticoes, te.observacoes
                FROM treinoexercicios te
                JOIN exercicios e ON te.id_exercicio = e.id_exercicio
                WHERE te.id_treino = %s
            """, (id_treino,))
            treino["exercicios"] = cursor.fetchall()

            return jsonify(treino), 200
    except Exception as e:
        print("Erro ao obter treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()

#=============================================
#Obter todos os detalhes dos treinos por aluno
#=============================================
@treinos_bp.route("/aluno/<int:id_aluno>/detalhes", methods=["GET"])
@jwt_required()
def detalhar_treinos_por_plano(id_aluno):
    identidade = extrair_user_info()
    tipo = identidade.get("tipo_usuario")
    id_logado = identidade.get("id")

    if tipo == "aluno" and id_logado != id_aluno:
        return jsonify({"message": "Acesso negado"}), 403
    elif tipo not in ["personal", "aluno"]:
        return jsonify({"message": "Apenas personal ou o próprio aluno podem acessar"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Buscar nome do aluno
            cursor.execute("SELECT nome, cpf FROM usuarios WHERE id_usuario = %s", (id_aluno,))
            aluno = cursor.fetchone()
            if not aluno:
                return jsonify({"message": "Aluno não encontrado"}), 404

            # Buscar todos os planos ativos do aluno
            cursor.execute("""
                SELECT id_plano, nome, data_criacao
                FROM planos_treino
                WHERE id_aluno = %s
                ORDER BY data_criacao DESC
            """, (id_aluno,))
            planos = cursor.fetchall()

            for plano in planos:
                cursor.execute("""
                    SELECT id_treino, nome_treino
                    FROM treinos
                    WHERE id_plano = %s AND ativo = TRUE
                """, (plano["id_plano"],))
                treinos = cursor.fetchall()

                for treino in treinos:
                    cursor.execute("""
                        SELECT e.nome, e.grupo_muscular, te.series, te.repeticoes, te.observacoes
                        FROM treinoexercicios te
                        JOIN exercicios e ON te.id_exercicio = e.id_exercicio
                        WHERE te.id_treino = %s
                    """, (treino["id_treino"],))
                    treino["exercicios"] = cursor.fetchall()

                plano["treinos"] = treinos

            return jsonify({
                "aluno": aluno,
                "planos_treino": planos
            }), 200
    except Exception as e:
        print("Erro ao detalhar planos de treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


#================================
#Função auxiliar para gerar o PDF
#================================
def buscar_dados_treino_completo(id_treino):
    db = get_db()
    with db.cursor() as cursor:
        # Obter informações principais do treino
        cursor.execute("""
            SELECT t.nome_treino, t.data_criacao, u.nome AS nome_aluno, u.email, u.whatsapp, u.id_usuario
            FROM treinos t
            JOIN usuarios u ON t.id_aluno = u.id_usuario
            WHERE t.id_treino = %s AND t.ativo = 1
        """, (id_treino,))
        treino = cursor.fetchone()
        if not treino:
            return None

        # Obter exercícios vinculados ao treino
        cursor.execute("""
            SELECT e.nome, e.grupo_muscular, te.series, te.repeticoes, te.observacoes
            FROM treinoexercicios te
            JOIN exercicios e ON te.id_exercicio = e.id_exercicio
            WHERE te.id_treino = %s
        """, (id_treino,))
        exercicios = cursor.fetchall()

        treino["exercicios"] = exercicios
        return treino
    
#==================
#Função Gerar PDF
#==================
def gerar_pdf_treino(treino, nome_arquivo="treino_temp.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marca d'água com logo no fundo
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        marca = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))
        c.drawImage(marca, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()
    except Exception as e:
        print(f"Erro ao carregar logo transparente: {e}")

    # Logo no topo
    try:
        c.drawImage(logo_path, 40, height - 80, width=60, height=60, mask='auto')
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    # Cabeçalho - dados do profissional
    c.setFont("Helvetica", 10)
    x_dados = 120
    y_dados = height - 50
    c.drawString(x_dados, y_dados, f"Profissional: {treino.get('nome_profissional', 'Não informado')}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"Telefone: {treino.get('telefone', 'Não informado')}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"E-mail: {treino.get('email', 'Não informado')}")

    # Linha separadora
    linha_y = y_dados - 10
    c.setLineWidth(1)
    c.line(40, linha_y, width - 40, linha_y)

    # Título do documento
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, linha_y - 30, "Ficha de Treino")

    # Dados do aluno
    y = linha_y - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, f"Aluno: {treino.get('nome_aluno', 'Não informado')}")
    y -= 20
    c.drawString(80, y, f"Treino: {treino.get('nome_treino', 'Sem nome')}")
    y -= 20

    # Lista de exercícios
    c.setFont("Helvetica-Bold", 11)
    c.drawString(80, y, "Exercícios:")
    y -= 15

    for ex in treino.get("exercicios", []):
        if y < 100:
            c.showPage()
            y = height - 80
        c.setFont("Helvetica-Bold", 10)
        c.drawString(90, y, f"{ex.get('nome', 'Exercício')} ({ex.get('grupo_muscular', '-')})")
        y -= 13
        c.setFont("Helvetica", 10)
        c.drawString(
            100,
            y,
            f"- Séries: {ex.get('series', '-')}  |  Repetições: {ex.get('repeticoes', '-')}  |  Observações: {ex.get('observacoes') or '-'}"
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
    
#=============================
#Função para dowload do PDF
#=============================
@treinos_bp.route("/<int:id_treino>/pdf", methods=["GET"])
@jwt_required()
@cross_origin()
def baixar_pdf_treino(id_treino):
    treino = buscar_dados_treino_completo(id_treino)
    if not treino:
        return jsonify({"message": "Treino não encontrado"}), 404

    try:
        pdf = gerar_pdf_treino(treino)
        return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name="treino.pdf")
    except Exception as e:
        print(f"[ERRO PDF] {e}")
        return jsonify({"message": "Erro ao gerar PDF"}), 500

#===========================
#Função enviar por e-mail
#===========================
@treinos_bp.route("/<int:id_treino>/enviar", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_treino(id_treino):
    try:
        treino = buscar_dados_treino_completo(id_treino)
        if not treino:
            return jsonify({"message": "Treino não encontrado"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT email, nome FROM usuarios WHERE id_usuario = %s", (treino["id_aluno"],))
            dados = cursor.fetchone()

        email = dados["email"] if dados and "email" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not email:
            return jsonify({"message": "E-mail do aluno não encontrado"}), 403

        try:
            pdf_stream = gerar_pdf_treino(treino)  # retorna BytesIO
        except Exception as e:
            print("Erro ao gerar PDF do treino:", e)
            registrar_log_envio(treino["id_aluno"], "email", email, "Erro ao gerar PDF do treino", "falha")
            return jsonify({"message": "Erro ao gerar o treino em PDF"}), 500

        try:
            msg = Message(
                subject="Seu Treino - Alpphas GYM",
                sender=None,
                recipients=[email],
                body=(
                    f"Olá {nome},\n\n"
                    f"Segue em anexo sua ficha de treino personalizada.\n\n"
                    f"Atenciosamente,\nEquipe Alpphas GYM"
                )
            )
            msg.attach(
                filename=f"treino_{id_treino}.pdf",
                content_type="application/pdf",
                data=pdf_stream.getvalue()
            )
            mail.send(msg)

            registrar_log_envio(treino["id_aluno"], "email", email, "Envio de ficha de treino em PDF", "sucesso")
            return jsonify({"message": "Treino enviado com sucesso por e-mail."}), 200

        except Exception as e:
            print("Erro ao enviar e-mail com treino:", e)
            registrar_log_envio(treino["id_aluno"], "email", email, "Erro ao enviar treino", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar o e-mail: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado ao enviar treino:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio do treino."}), 500

#=============================
#Rota para envio via WhatsApp
#=============================
@treinos_bp.route("/<int:id_treino>/enviar-whatsapp", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_treino_whatsapp(id_treino):
    try:
        treino = buscar_dados_treino_completo(id_treino)
        if not treino:
            return jsonify({"message": "Treino não encontrado"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT whatsapp, nome FROM usuarios WHERE id_usuario = %s", (treino["id_aluno"],))
            dados = cursor.fetchone()

        numero = dados["whatsapp"] if dados and "whatsapp" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not numero:
            return jsonify({"message": "WhatsApp do aluno não encontrado"}), 403

        # Gerar e salvar PDF temporário
        try:
            nome_arquivo = f"treino_{id_treino}.pdf"
            gerar_pdf_treino(treino, nome_arquivo=nome_arquivo, salvar_em_disco=True)
        except Exception as e:
            print("Erro ao gerar PDF do treino:", e)
            registrar_log_envio(treino["id_aluno"], "whatsapp", numero, "Erro ao gerar PDF do treino", "falha")
            return jsonify({"message": "Erro ao gerar o PDF do treino"}), 500

        url_base = os.getenv("APP_URL", "http://localhost:5000")
        url_pdf = f"{url_base}/treinos/{id_treino}/pdf"

        mensagem = (
            f"Olá {nome}, segue o link para sua ficha de treino personalizada:\n\n{url_pdf}\n\n"
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

            registrar_log_envio(treino["id_aluno"], "whatsapp", numero, mensagem, "sucesso")
            return jsonify({"message": "Treino enviado com sucesso via WhatsApp"}), 200

        except Exception as e:
            print("Erro ao enviar WhatsApp do treino:", e)
            registrar_log_envio(treino["id_aluno"], "whatsapp", numero, f"Erro no envio WhatsApp: {mensagem}", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar via WhatsApp: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado no envio:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio do treino via WhatsApp."}), 500
