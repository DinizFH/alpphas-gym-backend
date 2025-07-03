from flask import Blueprint, request, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
import json
from flask_cors import cross_origin
import os
from app.extensions.db import get_db
from app.utils.jwt import extrair_user_info
from app.utils.pdf_avaliacoes import gerar_pdf_avaliacao
from app.utils.email import enviar_email_com_anexo
from app.utils.whatsapp import enviar_whatsapp_com_arquivo
from app.utils.logs import registrar_log_envio

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

# ======================
# Exportar PDF da avaliação
# ======================
@avaliacoes_bp.route("/<int:id_avaliacao>/exportar", methods=["GET"])
@jwt_required()
@cross_origin()
def exportar_avaliacao(id_avaliacao):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["aluno", "personal", "nutricionista"]:
        return jsonify({"message": "Acesso não autorizado"}), 403

    try:
        caminho_pdf = gerar_pdf_avaliacao(id_avaliacao)
        if not caminho_pdf:
            return jsonify({"message": "Avaliação não encontrada"}), 404
        return send_file(caminho_pdf, as_attachment=True)
    except Exception as e:
        return jsonify({"message": "Erro ao gerar PDF", "erro": str(e)}), 500

# ======================
# Enviar por E-mail
# ======================
@avaliacoes_bp.route("/<int:id_avaliacao>/enviar-email", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_avaliacao_email(id_avaliacao):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({"message": "Apenas profissionais podem enviar avaliações"}), 403

    try:
        caminho_pdf = gerar_pdf_avaliacao(id_avaliacao)
        if not caminho_pdf:
            return jsonify({"message": "Avaliação não encontrada"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT email, nome FROM usuarios WHERE id_usuario = (SELECT id_aluno FROM avaliacoesfisicas WHERE id_avaliacao = %s)", (id_avaliacao,))
            dados = cursor.fetchone()

        if not dados or not dados.get("email"):
            return jsonify({"message": "E-mail do aluno não encontrado"}), 404

        assunto = "Avaliação Física - Alpphas GYM"
        mensagem = "Olá! Segue em anexo sua avaliação física realizada no Alpphas GYM."
        enviar_email_com_anexo(dados["email"], assunto, mensagem, caminho_pdf)

        registrar_log_envio(identidade["id_usuario"], "avaliacao", f"Avaliação enviada por e-mail para {dados['email']}", id_referencia=id_avaliacao)
        return jsonify({"message": "Avaliação enviada por e-mail com sucesso"})
    except Exception as e:
        return jsonify({"message": "Erro ao enviar e-mail", "erro": str(e)}), 500

# ======================
# Enviar por WhatsApp
# ======================
@avaliacoes_bp.route("/<int:id_avaliacao>/enviar-whatsapp", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_avaliacao_whatsapp(id_avaliacao):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({"message": "Apenas profissionais podem enviar avaliações"}), 403

    try:
        caminho_pdf = gerar_pdf_avaliacao(id_avaliacao)
        if not caminho_pdf:
            return jsonify({"message": "Avaliação não encontrada"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT whatsapp, nome FROM usuarios WHERE id_usuario = (SELECT id_aluno FROM avaliacoesfisicas WHERE id_avaliacao = %s)", (id_avaliacao,))
            dados = cursor.fetchone()

        numero = dados["whatsapp"] if dados and "whatsapp" in dados else None
        nome = dados["nome"] if dados and "nome" in dados else "Aluno"

        if not numero:
            return jsonify({"message": "WhatsApp do aluno não encontrado"}), 403

        mensagem = f"Olá {nome}, segue sua avaliação física realizada no Alpphas GYM."
        enviar_whatsapp_com_arquivo(numero, mensagem, caminho_pdf)

        registrar_log_envio(identidade["id_usuario"], "avaliacao", f"Avaliação enviada por WhatsApp para {numero}", id_referencia=id_avaliacao)
        return jsonify({"message": "Avaliação enviada por WhatsApp com sucesso"})
    except Exception as e:
        return jsonify({"message": "Erro ao enviar WhatsApp", "erro": str(e)}), 500

# ======================
# Enviar por E-mail e WhatsApp
# ======================
@avaliacoes_bp.route("/<int:id_avaliacao>/enviar-ambos", methods=["POST"])
@jwt_required()
@cross_origin()
def enviar_avaliacao_ambos(id_avaliacao):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({"message": "Apenas profissionais podem enviar avaliações"}), 403

    try:
        caminho_pdf = gerar_pdf_avaliacao(id_avaliacao)
        if not caminho_pdf:
            return jsonify({"message": "Avaliação não encontrada"}), 404

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT nome, email, whatsapp FROM usuarios WHERE id_usuario = (SELECT id_aluno FROM avaliacoesfisicas WHERE id_avaliacao = %s)", (id_avaliacao,))
            dados = cursor.fetchone()

        email = dados["email"]
        whatsapp = dados["whatsapp"]
        nome = dados["nome"]

        if not email and not whatsapp:
            return jsonify({"message": "Aluno sem e-mail e WhatsApp cadastrados"}), 403

        if email:
            assunto = "Avaliação Física - Alpphas GYM"
            mensagem = "Olá! Segue em anexo sua avaliação física realizada no Alpphas GYM."
            enviar_email_com_anexo(email, assunto, mensagem, caminho_pdf)
            registrar_log_envio(identidade["id_usuario"], "avaliacao", f"Avaliação enviada por e-mail para {email}", id_referencia=id_avaliacao)

        if whatsapp:
            mensagem_wpp = f"Olá {nome}, segue sua avaliação física realizada no Alpphas GYM."
            enviar_whatsapp_com_arquivo(whatsapp, mensagem_wpp, caminho_pdf)
            registrar_log_envio(identidade["id_usuario"], "avaliacao", f"Avaliação enviada por WhatsApp para {whatsapp}", id_referencia=id_avaliacao)

        return jsonify({"message": "Avaliação enviada com sucesso por e-mail e WhatsApp"})
    except Exception as e:
        return jsonify({"message": "Erro ao enviar avaliação", "erro": str(e)}), 500