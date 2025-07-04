from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.extensions.db import get_db
from app.utils.logs import registrar_log_envio

from io import BytesIO
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from flask_mail import Message
from app.extensions.mail import mail

import reportlab.lib.colors as rl_colors
import os, json, requests


avaliacoes_bp = Blueprint("avaliacoes", __name__)

def extrair_identidade():
    try:
        identidade_raw = get_jwt_identity()
        return json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
    except Exception as e:
        print(f"[ERRO] Falha ao extrair identidade do token: {e}")
        return None
    
# Função utilitária: buscar detalhes da avaliação por ID
def obter_avaliacao_por_id(id_avaliacao):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM avaliacoesfisicas WHERE id_avaliacao = %s", (id_avaliacao,))
        return cursor.fetchone()

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2) if altura else 0

def calcular_percentual_gordura(soma_dobras, idade):
    densidade = 1.10938 - 0.0008267 * soma_dobras + 0.0000016 * (soma_dobras ** 2) - 0.0002574 * idade
    return round((495 / densidade) - 450, 2)

def calcular_massa_gorda(peso, percentual_gordura):
    return round(peso * (percentual_gordura / 100), 2)

def calcular_massa_magra(peso, massa_gorda):
    return round(peso - massa_gorda, 2)

# ================================
# Criar avaliação (ATUALIZADA)
# ================================
@avaliacoes_bp.route("/", methods=["POST"])
@jwt_required()
def criar_avaliacao():
    identidade = extrair_identidade()
    if not identidade or identidade.get("tipo_usuario") == "aluno":
        return jsonify({"message": "Apenas profissionais podem criar avaliações"}), 403

    data = request.get_json()
    id_profissional = identidade.get("id")
    id_aluno = data.get("id_aluno")

    idade = data.get("idade")
    peso = data.get("peso")
    altura = data.get("altura")

    dobra_peitoral = data.get("dobra_peitoral")
    dobra_triceps = data.get("dobra_triceps")
    dobra_subescapular = data.get("dobra_subescapular")
    dobra_biceps = data.get("dobra_biceps")
    dobra_axilar_media = data.get("dobra_axilar_media")
    dobra_supra_iliaca = data.get("dobra_supra_iliaca")

    medidas = {
        "pescoco": data.get("pescoco"),
        "ombro": data.get("ombro"),
        "torax": data.get("torax"),
        "cintura": data.get("cintura"),
        "abdomen": data.get("abdomen"),
        "quadril": data.get("quadril"),
        "braco_direito": data.get("braco_direito"),
        "braco_esquerdo": data.get("braco_esquerdo"),
        "braco_d_contraido": data.get("braco_d_contraido"),
        "braco_e_contraido": data.get("braco_e_contraido"),
        "antebraco_direito": data.get("antebraco_direito"),
        "antebraco_esquerdo": data.get("antebraco_esquerdo"),
        "coxa_direita": data.get("coxa_direita"),
        "coxa_esquerda": data.get("coxa_esquerda"),
        "panturrilha_direita": data.get("panturrilha_direita"),
        "panturrilha_esquerda": data.get("panturrilha_esquerda")
    }

    observacoes = data.get("observacoes")

    if not all([id_aluno, idade, peso, altura, dobra_peitoral, dobra_triceps, dobra_subescapular, dobra_biceps, dobra_axilar_media, dobra_supra_iliaca]):
        return jsonify({"message": "Campos obrigatórios não fornecidos"}), 400

    soma_dobras = sum([
        dobra_peitoral, dobra_triceps, dobra_subescapular,
        dobra_biceps, dobra_axilar_media, dobra_supra_iliaca
    ])

    percentual_gordura = calcular_percentual_gordura(soma_dobras, idade)
    imc = calcular_imc(peso, altura)
    massa_gorda = calcular_massa_gorda(peso, percentual_gordura)
    massa_magra = calcular_massa_magra(peso, massa_gorda)

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO avaliacoesfisicas (
                    id_aluno, id_profissional, data_avaliacao, peso, altura, idade, imc,
                    percentual_gordura, massa_gorda, massa_magra,
                    pescoco, ombro, torax, cintura, abdomen, quadril,
                    braco_direito, braco_esquerdo, braco_d_contraido, braco_e_contraido,
                    antebraco_direito, antebraco_esquerdo,
                    coxa_direita, coxa_esquerda, panturrilha_direita, panturrilha_esquerda,
                    dobra_peitoral, dobra_triceps, dobra_subescapular, dobra_biceps,
                    dobra_axilar_media, dobra_supra_iliaca,
                    observacoes
                ) VALUES (
                    %s, %s, CURDATE(), %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s
                )
            """, (
                id_aluno, id_profissional, peso, altura, idade, imc,
                percentual_gordura, massa_gorda, massa_magra,
                medidas["pescoco"], medidas["ombro"], medidas["torax"], medidas["cintura"],
                medidas["abdomen"], medidas["quadril"], medidas["braco_direito"], medidas["braco_esquerdo"],
                medidas["braco_d_contraido"], medidas["braco_e_contraido"],
                medidas["antebraco_direito"], medidas["antebraco_esquerdo"],
                medidas["coxa_direita"], medidas["coxa_esquerda"],
                medidas["panturrilha_direita"], medidas["panturrilha_esquerda"],
                dobra_peitoral, dobra_triceps, dobra_subescapular, dobra_biceps,
                dobra_axilar_media, dobra_supra_iliaca,
                observacoes
            ))
            db.commit()
            return jsonify({"message": "Avaliação criada com sucesso"}), 201
    except Exception as e:
        print("Erro ao registrar avaliação:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()

# ================================
# Listar avaliações
# ================================
@avaliacoes_bp.route("/", methods=["GET"])
@jwt_required()
def listar_avaliacoes():
    identidade = extrair_identidade()
    if not identidade:
        return jsonify({"message": "Token inválido"}), 401

    user_id = identidade.get("id")
    tipo = identidade.get("tipo_usuario")

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "aluno":
                cursor.execute("""
                    SELECT a.*,
                    u1.nome AS nome_profissional,
                    u2.nome AS nome_aluno
                    FROM avaliacoesfisicas a
                    JOIN usuarios u1 ON u1.id_usuario = a.id_profissional
                    JOIN usuarios u2 ON u2.id_usuario = a.id_aluno
                    WHERE a.id_aluno = %s
                    ORDER BY a.data_avaliacao DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT a.*, 
                        u1.nome AS nome_aluno, u1.cpf AS cpf_aluno, 
                        u2.nome AS nome_profissional
                    FROM avaliacoesfisicas a
                    JOIN usuarios u1 ON u1.id_usuario = a.id_aluno
                    JOIN usuarios u2 ON u2.id_usuario = a.id_profissional
                    WHERE a.id_profissional = %s
                    ORDER BY a.data_avaliacao DESC
                """, (user_id,))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar avaliações:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# ================================
# Obter avaliação por ID (ATUALIZADA)
# ================================
@avaliacoes_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def obter_avaliacao(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.id_avaliacao, a.id_aluno, a.id_profissional,
                    a.peso, a.altura, a.idade, a.imc, a.percentual_gordura,
                    a.massa_gorda, a.massa_magra,
                    a.pescoco, a.ombro, a.torax, a.cintura, a.abdomen, a.quadril,
                    a.braco_direito, a.braco_esquerdo, a.braco_d_contraido, a.braco_e_contraido,
                    a.antebraco_direito, a.antebraco_esquerdo, a.coxa_direita, a.coxa_esquerda,
                    a.panturrilha_direita, a.panturrilha_esquerda,
                    a.dobra_peitoral, a.dobra_triceps, a.dobra_subescapular,
                    a.dobra_biceps, a.dobra_axilar_media, a.dobra_supra_iliaca,
                    a.observacoes,
                    u1.nome AS nome_aluno, u1.cpf AS cpf_aluno,
                    u2.nome AS nome_profissional
                FROM avaliacoesfisicas a
                JOIN usuarios u1 ON u1.id_usuario = a.id_aluno
                JOIN usuarios u2 ON u2.id_usuario = a.id_profissional
                WHERE a.id_avaliacao = %s
            """, (id,))
            avaliacao = cursor.fetchone()
            if not avaliacao:
                return jsonify({"message": "Avaliação não encontrada"}), 404
            return jsonify(avaliacao), 200
    except Exception as e:
        print("Erro ao buscar avaliação:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()



# ================================
# Editar avaliação
# ================================
@avaliacoes_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def editar_avaliacao(id):
    identidade = extrair_identidade()
    if not identidade or identidade.get("tipo_usuario") == "aluno":
        return jsonify({"message": "Apenas profissionais podem editar avaliações"}), 403

    user_id = identidade.get("id")
    data = request.get_json()
    print("DEBUG dados recebidos:", data)

    # Lista de campos esperados
    campos_esperados = [
        "peso", "altura", "idade", "dobra_peitoral", "dobra_triceps", "dobra_subescapular",
        "dobra_biceps", "dobra_axilar_media", "dobra_supra_iliaca", "imc", "percentual_gordura",
        "massa_gorda", "massa_magra", "pescoco", "ombro", "torax", "cintura", "abdomen", "quadril",
        "braco_direito", "braco_esquerdo", "braco_d_contraido", "braco_e_contraido",
        "antebraco_direito", "antebraco_esquerdo", "coxa_direita", "coxa_esquerda",
        "panturrilha_direita", "panturrilha_esquerda", "observacoes"
    ]

    # Converte campos vazios em None
    for campo in campos_esperados:
        if campo not in data:
            print(f"CAMPO FALTANDO: {campo}")
            return jsonify({"message": f"Campo obrigatório ausente: {campo}"}), 400
        if data[campo] == "":
            data[campo] = None

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Verifica se o usuário tem permissão para editar
            cursor.execute("SELECT id_profissional FROM avaliacoesfisicas WHERE id_avaliacao = %s", (id,))
            avaliacao = cursor.fetchone()
            if not avaliacao:
                return jsonify({"message": "Avaliação não encontrada"}), 404
            if avaliacao["id_profissional"] != user_id:
                return jsonify({"message": "Permissão negada"}), 403

            # Atualiza a avaliação
            cursor.execute("""
                UPDATE avaliacoesfisicas SET
                    peso = %s, altura = %s, idade = %s,
                    dobra_peitoral = %s, dobra_triceps = %s, dobra_subescapular = %s, 
                    dobra_biceps = %s, dobra_axilar_media = %s, dobra_supra_iliaca = %s,
                    imc = %s, percentual_gordura = %s, massa_gorda = %s, massa_magra = %s,
                    pescoco = %s, ombro = %s, torax = %s, cintura = %s, abdomen = %s, quadril = %s,
                    braco_direito = %s, braco_esquerdo = %s, braco_d_contraido = %s, braco_e_contraido = %s,
                    antebraco_direito = %s, antebraco_esquerdo = %s, coxa_direita = %s, coxa_esquerda = %s,
                    panturrilha_direita = %s, panturrilha_esquerda = %s, observacoes = %s
                WHERE id_avaliacao = %s
            """, (
                data["peso"], data["altura"], data["idade"],
                data["dobra_peitoral"], data["dobra_triceps"], data["dobra_subescapular"],
                data["dobra_biceps"], data["dobra_axilar_media"], data["dobra_supra_iliaca"],
                data["imc"], data["percentual_gordura"], data["massa_gorda"], data["massa_magra"],
                data["pescoco"], data["ombro"], data["torax"], data["cintura"], data["abdomen"], data["quadril"],
                data["braco_direito"], data["braco_esquerdo"], data["braco_d_contraido"], data["braco_e_contraido"],
                data["antebraco_direito"], data["antebraco_esquerdo"], data["coxa_direita"], data["coxa_esquerda"],
                data["panturrilha_direita"], data["panturrilha_esquerda"], data["observacoes"], id
            ))
            db.commit()
            return jsonify({"message": "Avaliação atualizada com sucesso"}), 200
    except Exception as e:
        print("Erro ao editar avaliação:", e)
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500
    finally:
        db.close()


# ================================
# Excluir avaliação
# ================================
@avaliacoes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def excluir_avaliacao(id):
    identidade = extrair_identidade()
    if not identidade or identidade.get("tipo_usuario") == "aluno":
        return jsonify({"message": "Apenas profissionais podem excluir avaliações"}), 403

    user_id = identidade.get("id")
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_profissional FROM avaliacoesfisicas WHERE id_avaliacao = %s", (id,))
            avaliacao = cursor.fetchone()
            if not avaliacao:
                return jsonify({"message": "Avaliação não encontrada"}), 404
            if avaliacao["id_profissional"] != user_id:
                return jsonify({"message": "Permissão negada"}), 403

            cursor.execute("DELETE FROM avaliacoesfisicas WHERE id_avaliacao = %s", (id,))
            db.commit()
            return jsonify({"message": "Avaliação excluída com sucesso"}), 200
    except Exception as e:
        print("Erro ao excluir avaliação:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()

# ================================
# Buscar aluno por nome
# ================================
@avaliacoes_bp.route("/buscar-aluno", methods=["GET"])
@jwt_required()
def buscar_aluno_por_nome():
    identidade = extrair_identidade()
    if not identidade or identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({"message": "Apenas profissionais podem buscar alunos"}), 403

    nome = request.args.get("nome", "").strip()
    if not nome:
        return jsonify({"message": "Parâmetro 'nome' é obrigatório"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nome, email, cpf
                FROM usuarios
                WHERE tipo_usuario = 'aluno' AND nome LIKE %s AND ativo = TRUE
            """, (f"%{nome}%",))
            alunos = cursor.fetchall()
            return jsonify(alunos), 200
    except Exception as e:
        print("Erro ao buscar aluno:", e)
        return jsonify({"message": "Erro interno ao buscar aluno"}), 500
    finally:
        db.close()

# ================================
# Evolução (com novos campos)
# ================================
@avaliacoes_bp.route("/evolucao/<int:id_aluno>", methods=["GET"])
@jwt_required()
def evolucao_avaliacoes(id_aluno):
    identidade = extrair_identidade()
    if not identidade:
        return jsonify({"message": "Token inválido"}), 401

    tipo = identidade.get("tipo_usuario")
    id_usuario = identidade.get("id")

    # Aluno só pode acessar os próprios dados
    if tipo == "aluno" and id_usuario != id_aluno:
        return jsonify({"message": "Permissão negada"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT nome, cpf FROM usuarios WHERE id_usuario = %s", (id_aluno,))
            aluno = cursor.fetchone()
            if not aluno:
                return jsonify({"message": "Aluno não encontrado"}), 404

            cursor.execute("""
                SELECT 
                    data_avaliacao, imc, percentual_gordura, massa_gorda, massa_magra,
                    ombro, torax, cintura, abdomen, quadril,
                    braco_direito, braco_esquerdo,
                    braco_d_contraido, braco_e_contraido,
                    antebraco_direito, antebraco_esquerdo,
                    coxa_direita, coxa_esquerda,
                    panturrilha_direita, panturrilha_esquerda,
                    dobra_peitoral, dobra_triceps, dobra_subescapular,
                    dobra_biceps, dobra_axilar_media, dobra_supra_iliaca
                FROM avaliacoesfisicas
                WHERE id_aluno = %s
                ORDER BY data_avaliacao ASC
            """, (id_aluno,))
            avals = cursor.fetchall()

            return jsonify({
                "aluno": {
                    "id": id_aluno,
                    "nome": aluno["nome"],
                    "cpf": aluno["cpf"]
                },
                "avaliacoes": avals
            }), 200
    except Exception as e:
        print("Erro ao buscar evolução:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()

#============================================
# Função detalhar_avaliacao_para_uso (completa)
#============================================
def detalhar_avaliacao_para_uso(id_avaliacao):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                a.id_aluno,
                u1.nome AS nome_aluno,
                u2.nome AS nome_profissional,
                u2.email, u2.telefone, u2.endereco, u2.cref,
                a.data_avaliacao, a.idade, a.peso, a.altura, a.percentual_gordura,
                a.dobra_peitoral, a.dobra_triceps, a.dobra_subescapular,
                a.dobra_biceps, a.dobra_axilar_media, a.dobra_supra_iliaca,
                a.pescoco, a.ombro, a.torax, a.cintura, a.abdomen, a.quadril,
                a.braco_direito, a.braco_esquerdo, a.braco_d_contraido, a.braco_e_contraido,
                a.antebraco_direito, a.antebraco_esquerdo,
                a.coxa_direita, a.coxa_esquerda,
                a.panturrilha_direita, a.panturrilha_esquerda
            FROM avaliacoesfisicas a
            JOIN usuarios u1 ON a.id_aluno = u1.id_usuario
            JOIN usuarios u2 ON a.id_profissional = u2.id_usuario
            WHERE a.id_avaliacao = %s
        """, (id_avaliacao,))
        avaliacao_principal = cursor.fetchone()

        if not avaliacao_principal:
            return None

        id_aluno = avaliacao_principal["id_aluno"]

        cursor.execute("""
            SELECT data_avaliacao, percentual_gordura
            FROM avaliacoesfisicas
            WHERE id_aluno = %s
            ORDER BY data_avaliacao ASC
            LIMIT 3
        """, (id_aluno,))
        historico = cursor.fetchall()

        todas = []
        for h in historico:
            nova = {
                "nome_aluno": avaliacao_principal["nome_aluno"],
                "nome_profissional": avaliacao_principal["nome_profissional"],
                "email": avaliacao_principal["email"],
                "telefone": avaliacao_principal["telefone"],
                "endereco": avaliacao_principal["endereco"],
                "cref": avaliacao_principal["cref"],
                "data_avaliacao": h["data_avaliacao"],
                "percentual_gordura": h["percentual_gordura"]
            }
            if h["data_avaliacao"] == avaliacao_principal["data_avaliacao"]:
                nova.update(avaliacao_principal)
            todas.append(nova)

        return todas

#=================================
# Gerar PDF
#=================================
def gerar_pdf_avaliacao(avaliacoes, nome_arquivo="avaliacao_temp.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    atual = avaliacoes[-1]  # Última avaliação

    # Marca d'água (logo central transparente)
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        watermark = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))
        c.drawImage(watermark, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()
    except:
        pass

    # Logo no canto superior
    try:
        c.drawImage(logo_path, 40, height - 80, width=60, height=60, mask='auto')
    except:
        pass

    # Cabeçalho do profissional
    c.setFont("Helvetica", 10)
    x_dados = 120
    y_dados = height - 50
    c.drawString(x_dados, y_dados, f"Profissional: {atual['nome_profissional']}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"Telefone: {atual.get('telefone') or 'Não informado'}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"E-mail: {atual.get('email') or 'Não informado'}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"CREF: {atual.get('cref') or 'Não informado'}")

    c.setLineWidth(1)
    linha_y = y_dados - 10
    c.line(40, linha_y, width - 40, linha_y)

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, linha_y - 30, "Avaliação Física")

    # Dados do aluno
    y = linha_y - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, f"Aluno: {atual['nome_aluno']}")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(80, y, f"Data: {atual['data_avaliacao'].strftime('%d/%m/%Y')}")
    y -= 15
    c.drawString(80, y, f"Peso: {atual['peso']} kg    Altura: {atual['altura']} m")
    y -= 25

    # Medidas corporais
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, "Medições corporais:")
    y -= 15
    c.setFont("Helvetica", 10)
    medidas = [
        ("Ombro", "ombro"),
        ("Tórax", "torax"),
        ("Cintura", "cintura"),
        ("Abdômen", "abdomen"),
        ("Quadril", "quadril"),
        ("Braço Direito", "braco_direito"),
        ("Braço Esquerdo", "braco_esquerdo"),
        ("Braço D. Contraído", "braco_d_contraido"),
        ("Braço E. Contraído", "braco_e_contraido"),
        ("Antebraço Direito", "antebraco_direito"),
        ("Antebraço Esquerdo", "antebraco_esquerdo"),
        ("Coxa Direita", "coxa_direita"),
        ("Coxa Esquerda", "coxa_esquerda"),
        ("Panturrilha Direita", "panturrilha_direita"),
        ("Panturrilha Esquerda", "panturrilha_esquerda"),
    ]
    for label, key in medidas:
        if y < 100:
            c.showPage()
            y = height - 80
        c.drawString(100, y, f"- {label}: {atual.get(key, '---')} cm")
        y -= 13

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, "Dobras cutâneas:")
    y -= 15
    c.setFont("Helvetica", 10)
    dobras = [
        ("Peitoral", "dobra_peitoral"),
        ("Tríceps", "dobra_triceps"),
        ("Subescapular", "dobra_subescapular"),
        ("Bíceps", "dobra_biceps"),
        ("Axilar Média", "dobra_axilar_media"),
        ("Supra-ilíaca", "dobra_supra_iliaca"),
    ]
    for label, key in dobras:
        if y < 100:
            c.showPage()
            y = height - 80
        c.drawString(100, y, f"- {label}: {atual.get(key, '---')} mm")
        y -= 13

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, f"Percentual de Gordura: {atual.get('percentual_gordura', '---')}%")

    # Página nova para gráfico
    c.showPage()

    drawing = Drawing(500, 250)

    # Gráfico de evolução de % gordura (até 3 avaliações)
    dados = []
    labels = []
    for i, a in enumerate(avaliacoes):
        try:
            pg = float(a["percentual_gordura"])
            dados.append((i + 1, pg))
            labels.append(a["data_avaliacao"].strftime("%d/%m"))
        except:
            continue

    if dados:
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.height = 150
        lp.width = 400
        lp.data = [dados]
        lp.lines[0].strokeColor = rl_colors.HexColor("#0072C6")
        lp.lineLabelFormat = '%2.1f'
        lp.strokeColor = rl_colors.black
        lp.joinedLines = 1
        lp.xValueAxis.valueMin = 1
        lp.xValueAxis.valueMax = max(3, len(dados))
        lp.xValueAxis.valueStep = 1
        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueMax = max([y for _, y in dados] + [25])
        lp.yValueAxis.valueStep = 5

        drawing.add(lp)

        # Título do gráfico
        title = Label()
        title.setOrigin(250, 220)
        title.boxAnchor = 'n'
        title.setText("Evolução do Percentual de Gordura")
        title.fontSize = 14
        drawing.add(title)

        # Legenda com datas
        for i, label in enumerate(labels):
            drawing.add(String(50 + i * 130, 40, label, fontSize=9))

        drawing.drawOn(c, 40, height - 320)

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

    
#==============================
#Visualização e Download do PDF
#==============================
@avaliacoes_bp.route("/<int:id_avaliacao>/pdf", methods=["GET"])
@jwt_required()
@cross_origin()
def baixar_pdf_avaliacao(id_avaliacao):
    avaliacoes = detalhar_avaliacao_para_uso(id_avaliacao)
    if not avaliacoes or len(avaliacoes) == 0:
        return jsonify({"message": "Avaliação não encontrada"}), 404

    try:
        pdf = gerar_pdf_avaliacao(avaliacoes)
        return send_file(
            pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"avaliacao_fisica_{id_avaliacao}.pdf"
        )
    except Exception as e:
        print(f"[ERRO PDF AVALIACAO] {e}")
        return jsonify({"message": "Erro ao gerar PDF da avaliação física"}), 500

    
#=======================
#Envio via WhatsApp
#=======================
@avaliacoes_bp.route("/<int:id_avaliacao>/enviar-whatsapp", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_avaliacao_whatsapp(id_avaliacao):
    try:
        avaliacoes = detalhar_avaliacao_para_uso(id_avaliacao)
        if not avaliacoes or len(avaliacoes) == 0:
            return jsonify({"message": "Avaliação não encontrada"}), 404

        atual = avaliacoes[-1]  # avaliação mais recente (com dados completos)

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT whatsapp, nome FROM usuarios WHERE id_usuario = %s", (atual["id_aluno"],))
            dados = cursor.fetchone()

        numero = dados["whatsapp"] if dados and "whatsapp" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not numero:
            return jsonify({"message": "WhatsApp do aluno não encontrado"}), 403

        # Gerar e salvar PDF
        try:
            nome_arquivo = f"avaliacao_{id_avaliacao}.pdf"
            gerar_pdf_avaliacao(avaliacoes, nome_arquivo=nome_arquivo, salvar_em_disco=True)
        except Exception as e:
            print("Erro ao gerar PDF:", e)
            registrar_log_envio(atual["id_aluno"], "whatsapp", numero, "Erro ao gerar PDF", "falha")
            return jsonify({"message": "Erro ao gerar o PDF da avaliação"}), 500

        url_base = os.getenv("APP_URL", "http://localhost:5000")
        url_pdf = f"{url_base}/avaliacoes/{id_avaliacao}/pdf"

        mensagem = (
            f"Olá {nome}, segue o link para sua avaliação física personalizada:\n\n{url_pdf}\n\n"
            f"Equipe Alpphas GYM"
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

            registrar_log_envio(atual["id_aluno"], "whatsapp", numero, mensagem, "sucesso")
            return jsonify({"message": "Avaliação enviada com sucesso via WhatsApp"}), 200

        except Exception as e:
            print("Erro ao enviar WhatsApp:", e)
            registrar_log_envio(atual["id_aluno"], "whatsapp", numero, f"Erro no envio WhatsApp: {mensagem}", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar via WhatsApp: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado no envio:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio via WhatsApp."}), 500

#=====================
#Envio via E-mail
#=====================
@avaliacoes_bp.route("/<int:id_avaliacao>/enviar", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_avaliacao_email(id_avaliacao):
    try:
        avaliacoes = detalhar_avaliacao_para_uso(id_avaliacao)
        if not avaliacoes or len(avaliacoes) == 0:
            return jsonify({"message": "Avaliação não encontrada"}), 404

        atual = avaliacoes[-1]  # avaliação atual com dados completos

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT email, nome FROM usuarios WHERE id_usuario = %s", (atual["id_aluno"],))
            dados = cursor.fetchone()

        email = dados["email"] if dados and "email" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not email:
            return jsonify({"message": "E-mail do aluno não encontrado"}), 403

        # Gerar PDF da avaliação
        try:
            pdf_stream = gerar_pdf_avaliacao(avaliacoes)
            pdf_data = pdf_stream.read()  # necessário para garantir que não está no início
            pdf_stream.seek(0)  # garantir que a leitura esteja no ponto inicial
        except Exception as e:
            print("Erro ao gerar PDF:", e)
            registrar_log_envio(atual["id_aluno"], "email", email, "Erro ao gerar PDF", "falha")
            return jsonify({"message": "Erro ao gerar o PDF da avaliação"}), 500

        # Preparar e enviar o e-mail
        try:
            msg = Message(
                subject="📋 Sua Avaliação Física - Alpphas GYM",
                recipients=[email],
                body=(
                    f"Olá {nome},\n\n"
                    f"Segue em anexo o arquivo da sua avaliação física personalizada com gráfico de evolução.\n\n"
                    f"Qualquer dúvida, entre em contato com seu profissional.\n\n"
                    f"Atenciosamente,\nEquipe Alpphas GYM"
                )
            )

            msg.attach(
                filename=f"avaliacao_fisica_{id_avaliacao}.pdf",
                content_type="application/pdf",
                data=pdf_data
            )

            mail.send(msg)

            registrar_log_envio(atual["id_aluno"], "email", email, "Envio de avaliação física em PDF", "sucesso")
            return jsonify({"message": "Avaliação enviada com sucesso por e-mail."}), 200

        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            registrar_log_envio(atual["id_aluno"], "email", email, "Erro ao enviar avaliação física", f"falha: {str(e)}")
            return jsonify({"message": f"Erro ao enviar o e-mail: {str(e)}"}), 500

    except Exception as e:
        print("Erro inesperado no envio:", e)
        return jsonify({"message": "Erro inesperado ao processar o envio da avaliação."}), 500
