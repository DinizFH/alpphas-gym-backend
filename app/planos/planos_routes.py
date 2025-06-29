import os, requests
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from app.utils.log_admin import registrar_log_admin

from app.extensions.db import get_db
from app.extensions.mail import mail
from app.utils.jwt import extrair_user_info
from flask_mail import Message


planos_bp = Blueprint("planos", __name__)

# --------------------------------------------------
# Buscar aluno por nome
# --------------------------------------------------
@planos_bp.route("/buscar-aluno", methods=["GET"])
@jwt_required()
def buscar_aluno_por_nome():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "nutricionista":
        return jsonify({"message": "Apenas nutricionistas podem buscar alunos"}), 403

    nome = request.args.get("nome", "").strip()
    if not nome:
        return jsonify({"message": "Parâmetro 'nome' é obrigatório"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nome, cpf, email, whatsapp
                FROM usuarios
                WHERE tipo_usuario = 'aluno' AND nome LIKE %s AND ativo = TRUE
            """, (f"%{nome}%",))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar aluno: {str(e)}"}), 500


# --------------------------------------------------
# Criar plano alimentar
# --------------------------------------------------
@planos_bp.route("/", methods=["POST"])
@jwt_required()
def criar_plano():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "nutricionista":
        return jsonify({"message": "Apenas nutricionistas podem criar planos"}), 403

    data = request.get_json()
    id_aluno = data.get("id_aluno")
    refeicoes = data.get("refeicoes", [])

    if not id_aluno or not refeicoes:
        return jsonify({"message": "Dados obrigatórios ausentes"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Verifica se o aluno existe
            cursor.execute(
                "SELECT id_usuario FROM usuarios WHERE id_usuario=%s AND tipo_usuario='aluno'",
                (id_aluno,)
            )
            if not cursor.fetchone():
                return jsonify({"message": "Aluno não encontrado"}), 404

            # Cria plano
            cursor.execute("""
                INSERT INTO planosalimentares (id_aluno, id_nutricionista, ativo)
                VALUES (%s, %s, TRUE)
            """, (id_aluno, identidade["id"]))
            id_plano = cursor.lastrowid

            # Refeições e alimentos
            for r in refeicoes:
                cursor.execute("""
                    INSERT INTO refeicoes (id_plano, titulo, calorias_estimadas)
                    VALUES (%s, %s, %s)
                """, (id_plano, r["titulo"], r["calorias_estimadas"]))
                id_refeicao = cursor.lastrowid

                for alimento in r.get("alimentos", []):
                    nome = str(alimento.get("nome", "")).strip()
                    peso = str(alimento.get("peso", "")).strip()

                    if not nome or not peso:
                        continue

                    cursor.execute("""
                        INSERT INTO alimentos (id_refeicao, nome, peso)
                        VALUES (%s, %s, %s)
                    """, (id_refeicao, nome, peso))

            db.commit()
            return jsonify({"message": "Plano criado com sucesso", "id_plano": id_plano}), 201

    except Exception as e:
        db.rollback()
        print("Erro ao criar plano:", e)
        return jsonify({"message": f"Erro ao criar plano: {str(e)}"}), 500

# --------------------------------------------------
# Editar plano alimentar
# --------------------------------------------------
@planos_bp.route("/<int:id_plano>", methods=["PUT"])
@jwt_required()
def editar_plano(id_plano):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "nutricionista":
        return jsonify({"message": "Apenas nutricionistas podem editar planos"}), 403

    data = request.get_json()
    refeicoes = data.get("refeicoes", [])
    if not refeicoes:
        return jsonify({"message": "Refeições são obrigatórias"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # plano pertence a este nutri?
            cursor.execute("""
                SELECT id_plano FROM planosalimentares
                WHERE id_plano=%s AND id_nutricionista=%s AND ativo=TRUE
            """, (id_plano, identidade["id"]))
            if not cursor.fetchone():
                return jsonify({"message": "Plano não encontrado ou acesso negado"}), 403

            # apagar refeições/alimentos antigos
            cursor.execute("SELECT id_refeicao FROM refeicoes WHERE id_plano=%s", (id_plano,))
            for ref_ant in cursor.fetchall():
                cursor.execute("DELETE FROM alimentos WHERE id_refeicao=%s", (ref_ant["id_refeicao"],))
            cursor.execute("DELETE FROM refeicoes WHERE id_plano=%s", (id_plano,))

            # inserir novas refeições e alimentos
            for r in refeicoes:
                cursor.execute("""
                    INSERT INTO refeicoes (id_plano, titulo, calorias_estimadas)
                    VALUES (%s, %s, %s)
                """, (id_plano, r["titulo"], r["calorias_estimadas"]))
                id_refeicao = cursor.lastrowid

                for alimento in r.get("alimentos", []):
                    nome = str(alimento.get("nome", "")).strip()
                    peso = str(alimento.get("peso", "")).strip()

                    if not nome or not peso:
                        continue

                    cursor.execute("""
                        INSERT INTO alimentos (id_refeicao, nome, peso)
                        VALUES (%s, %s, %s)
                    """, (id_refeicao, nome, peso))

            db.commit()
            return jsonify({"message": "Plano atualizado com sucesso"}), 200

    except Exception as e:
        db.rollback()
        print("Erro ao editar plano:", e)
        return jsonify({"message": f"Erro ao editar plano: {str(e)}"}), 500

# --------------------------------------------------
# Listar planos (com data + 1º título)
# --------------------------------------------------
@planos_bp.route("/", methods=["GET"])
@jwt_required()
def listar_planos():
    identidade = extrair_user_info()
    user_id = identidade["id"]
    tipo    = identidade["tipo_usuario"]

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "aluno":
                cursor.execute("""
                    SELECT 
                        p.id_plano,
                        u1.nome AS nome_aluno,
                        u2.nome AS nome_profissional,
                        p.data_criacao,
                        MIN(r.titulo) AS titulo_refeicao
                    FROM planosalimentares p
                    JOIN usuarios u1 ON p.id_aluno = u1.id_usuario
                    JOIN usuarios u2 ON p.id_nutricionista = u2.id_usuario
                    LEFT JOIN refeicoes r ON r.id_plano = p.id_plano
                    WHERE p.id_aluno = %s AND p.ativo = TRUE
                    GROUP BY p.id_plano
                """, (user_id,))
            elif tipo == "nutricionista":
                cursor.execute("""
                    SELECT 
                        p.id_plano,
                        u1.nome AS nome_aluno,
                        u2.nome AS nome_profissional,
                        p.data_criacao,
                        MIN(r.titulo) AS titulo_refeicao
                    FROM planosalimentares p
                    JOIN usuarios u1 ON p.id_aluno = u1.id_usuario
                    JOIN usuarios u2 ON p.id_nutricionista = u2.id_usuario
                    LEFT JOIN refeicoes r ON r.id_plano = p.id_plano
                    WHERE p.id_nutricionista = %s AND p.ativo = TRUE
                    GROUP BY p.id_plano
                """, (user_id,))
            else:
                return jsonify({"message": "Tipo de usuário não autorizado"}), 403

            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("[ERRO] Falha ao listar planos:", e)
        return jsonify({"message": f"Erro ao listar planos: {str(e)}"}), 500



# --------------------------------------------------
# Detalhar plano alimentar com refeições e alimentos
# --------------------------------------------------
@planos_bp.route("/<int:id_plano>", methods=["GET"])
@jwt_required()
def detalhar_plano_para_uso(id_plano):
    db = get_db()
    with db.cursor() as cursor:
        # Buscar dados do plano + nutricionista + aluno
        cursor.execute("""
            SELECT u1.nome AS nome_aluno,
                   u2.nome AS nome_profissional,
                   u2.email, u2.telefone, u2.endereco, u2.crn
            FROM planosalimentares p
            JOIN usuarios u1 ON p.id_aluno = u1.id_usuario
            JOIN usuarios u2 ON p.id_nutricionista = u2.id_usuario
            WHERE p.id_plano=%s AND p.ativo=TRUE
        """, (id_plano,))
        plano = cursor.fetchone()

        if not plano:
            return jsonify({"message": "Plano não encontrado"}), 404

        # Buscar refeições
        cursor.execute("""
            SELECT id_refeicao, titulo, calorias_estimadas
            FROM refeicoes
            WHERE id_plano=%s
            ORDER BY id_refeicao
        """, (id_plano,))
        refeicoes = cursor.fetchall()

        # Buscar alimentos para cada refeição
        for r in refeicoes:
            cursor.execute("""
                SELECT nome, peso
                FROM alimentos
                WHERE id_refeicao=%s AND nome IS NOT NULL AND peso IS NOT NULL
                ORDER BY id_alimento
            """, (r["id_refeicao"],))
            r["alimentos"] = cursor.fetchall()

        plano["refeicoes"] = refeicoes
        return jsonify(plano), 200


# --------------------------------------------------
# Desativar plano
# --------------------------------------------------
@planos_bp.route("/<int:id_plano>", methods=["DELETE"])
@jwt_required()
def excluir_plano(id_plano):
    identidade = extrair_user_info()
    if identidade["tipo_usuario"] != "nutricionista":
        return jsonify({"message": "Apenas nutricionistas podem excluir planos"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE planosalimentares SET ativo=FALSE WHERE id_plano=%s", (id_plano,))
            db.commit()
            return jsonify({"message": "Plano desativado"}), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao desativar plano: {str(e)}"}), 500


# =======================
# Enviar plano por e-mail (anexo PDF)
# =======================
@planos_bp.route("/<int:id_plano>/enviar", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_plano(id_plano):
    try:
        plano = detalhar_plano_para_uso(id_plano)
        if not plano:
            return jsonify({"message": "Plano não encontrado"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT email, nome FROM usuarios WHERE id_usuario = %s", (plano["id_aluno"],))
            dados = cursor.fetchone()

        email = dados["email"] if dados and "email" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not email:
            return jsonify({"message": "E-mail do aluno não encontrado"}), 403

        # Geração segura do PDF
        try:
            pdf_stream = gerar_pdf_plano(plano)  # já retorna um BytesIO
        except Exception as e:
            print("Erro ao gerar PDF:", e)
            return jsonify({"message": "Erro ao gerar o plano em PDF"}), 500

        # Envio do e-mail
        try:
            msg = Message(
                subject="Seu Plano Alimentar - Alpphas GYM",
                sender=None,  # usa o MAIL_DEFAULT_SENDER do .env
                recipients=[email],
                body=(
                    f"Olá {nome},\n\n"
                    f"Segue em anexo o seu plano alimentar personalizado.\n\n"
                    f"Atenciosamente,\nEquipe Alpphas GYM"
                )
            )
            msg.attach(
                filename=f"plano_alimentar_{id_plano}.pdf",
                content_type="application/pdf",
                data=pdf_stream.getvalue()  # CORREÇÃO: pega os bytes do stream
            )
            mail.send(msg)
            return jsonify({"message": "Plano enviado com sucesso por e-mail."}), 200

        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            return jsonify({"message": f"Erro ao enviar o e-mail: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado no envio:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio do plano."}), 500


# =======================
# Função auxiliar
# =======================
def detalhar_plano_para_uso(id_plano):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT p.id_aluno,
                   u1.nome AS nome_aluno,
                   u2.nome AS nome_profissional,
                   u2.email, u2.telefone, u2.endereco, u2.crn
            FROM planosalimentares p
            JOIN usuarios u1 ON p.id_aluno = u1.id_usuario
            JOIN usuarios u2 ON p.id_nutricionista = u2.id_usuario
            WHERE p.id_plano = %s
        """, (id_plano,))

        plano = cursor.fetchone()
        if not plano:
            return None

        cursor.execute("SELECT * FROM refeicoes WHERE id_plano = %s", (id_plano,))
        refeicoes = cursor.fetchall()
        for r in refeicoes:
            cursor.execute("SELECT nome, peso FROM alimentos WHERE id_refeicao = %s", (r["id_refeicao"],))
            r["alimentos"] = cursor.fetchall()
        plano["refeicoes"] = refeicoes
        return plano


# =======================
# Gerar PDF do plano
# =======================

@planos_bp.route("/<int:id_plano>/pdf", methods=["GET"])
@jwt_required()
@cross_origin()
def baixar_pdf(id_plano):
    plano = detalhar_plano_para_uso(id_plano)
    if not plano:
        return jsonify({"message": "Plano não encontrado"}), 404

    try:
        pdf = gerar_pdf_plano(plano)
        return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name="plano_alimentar.pdf")
    except Exception as e:
        print(f"[ERRO PDF] {e}")
        return jsonify({"message": "Erro ao gerar PDF"}), 500


def gerar_pdf_plano(plano, nome_arquivo="plano_temp.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marca d'água com logo central e transparente
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        watermark = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))  # Mais suave
        c.drawImage(watermark, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()
    except Exception as e:
        print(f"Erro ao carregar logo transparente: {e}")

    # Cabeçalho com logo no canto superior esquerdo
    try:
        c.drawImage(logo_path, 40, height - 80, width=60, height=60, mask='auto')
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    # Dados do nutricionista
    c.setFont("Helvetica", 10)
    x_dados = 120
    y_dados = height - 50
    c.drawString(x_dados, y_dados, f"Nutricionista: {plano['nome_profissional']}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"Telefone: {plano.get('telefone') or 'Não informado'}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"E-mail: {plano.get('email') or 'Não informado'}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"CRN: {plano.get('crn') or 'Não informado'}")

    # Linha horizontal
    linha_y = y_dados - 10
    c.setLineWidth(1)
    c.line(40, linha_y, width - 40, linha_y)

    # Título centralizado
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, linha_y - 30, "Plano Alimentar")

    # Dados do aluno
    y = linha_y - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, f"Aluno: {plano['nome_aluno']}")
    y -= 20

    # Refeições
    c.setFont("Helvetica", 11)
    for r in plano["refeicoes"]:
        if y < 100:
            c.showPage()
            y = height - 80
        c.setFont("Helvetica-Bold", 11)
        c.drawString(80, y, f"Refeição: {r['titulo']} ({r['calorias_estimadas']} kcal)")
        y -= 15
        c.setFont("Helvetica", 10)
        for a in r["alimentos"]:
            c.drawString(100, y, f"- {a['nome']} - {a['peso']}")
            y -= 13
        y -= 10

    c.save()
    buffer.seek(0)

    if salvar_em_disco:
        caminho = os.path.join("app", "static", "pdfs", nome_arquivo)

        # ✅ Garante que a pasta exista antes de salvar
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        with open(caminho, "wb") as f:
            f.write(buffer.getbuffer())
        return caminho
    else:
        return buffer

# ==============================
# Função Enviar para o WhatsApp 
# ==============================
@planos_bp.route("/<int:id_plano>/enviar-whatsapp", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_plano_whatsapp(id_plano):
    plano = detalhar_plano_para_uso(id_plano)
    if not plano:
        return jsonify({"message": "Plano não encontrado"}), 404

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT whatsapp FROM usuarios WHERE id_usuario = %s", (plano["id_aluno"],))
        dados = cursor.fetchone()
        whatsapp = dados["whatsapp"] if dados and "whatsapp" in dados else None

    if not whatsapp:
        return jsonify({"message": "WhatsApp do aluno não encontrado"}), 403

    nome_arquivo = f"plano_{id_plano}.pdf"
    try:
        caminho_pdf = gerar_pdf_plano(plano, nome_arquivo=nome_arquivo, salvar_em_disco=True)
        print(f"[PDF] Salvo com sucesso em: {caminho_pdf}")
    except Exception as e:
        print(f"[ERRO AO GERAR PDF]: {e}")
        return jsonify({"message": "Erro ao gerar PDF"}), 500

    servidor = os.getenv("APP_URL", "http://localhost:5000")
    pdf_url = f"{servidor}/static/pdfs/{nome_arquivo}"

    mensagem = f"Olá! Segue o link para acessar seu Plano Alimentar personalizado pelo Alpphas GYM 💪\n{pdf_url}"

    ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
    ULTRAMSG_INSTANCE = os.getenv("ULTRAMSG_INSTANCE")

    if not ULTRAMSG_TOKEN or not ULTRAMSG_INSTANCE:
        return jsonify({"message": "Configuração UltraMsg ausente"}), 500

    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat?token={ULTRAMSG_TOKEN}"
    payload = {
        "to": whatsapp,
        "body": mensagem
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"[ULTRAMSG] Status: {response.status_code}")
        print(f"[ULTRAMSG] Response: {response.text}")

        if response.status_code == 200 and "error" not in response.text.lower():
            usuario = get_jwt_identity()
            registrar_log_admin(f"Enviou plano {id_plano} via WhatsApp", usuario_id=usuario["id"])
            return jsonify({"message": "Plano enviado com sucesso via WhatsApp"}), 200
        else:
            return jsonify({
                "message": "Erro ao enviar mensagem via WhatsApp",
                "detalhes": response.text
            }), 500
    except Exception as e:
        return jsonify({"message": f"Falha na comunicação com UltraMsg: {str(e)}"}), 500
