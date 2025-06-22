from flask import Blueprint, jsonify
from app.extensions.db import get_db

utils_bp = Blueprint("utils", __name__)

@utils_bp.route("/utils/limpar", methods=["POST"])
def limpar_banco():
    db = get_db()
    if db is None:
        return jsonify({"msg": "Erro ao conectar ao banco"}), 500

    tabelas = [
        "registrostreino",
        "refeicoes",
        "planosalimentares",
        "avaliacoesfisicas",
        "agendamentos",
        "treinoexercicios",
        "treinos",
        "exercicios",
        "usuarios"
    ]

    try:
        with db.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for tabela in tabelas:
                cursor.execute(f"DELETE FROM {tabela};")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        db.commit()
        return jsonify({"msg": "Banco limpo com sucesso"}), 200
    except Exception as e:
        print("Erro ao limpar banco:", e)
        return jsonify({"msg": "Erro ao limpar banco"}), 500
    finally:
        db.close()
