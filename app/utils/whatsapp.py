import os
import requests
from app.utils.logs import registrar_log_envio

def enviar_avaliacao_por_whatsapp(avaliacao, url_pdf):
    """
    Envia o link da avaliação física via WhatsApp para o aluno.

    Parâmetros:
    - avaliacao: dict retornado por detalhar_avaliacao_para_uso
    - url_pdf: URL completa do PDF gerado (ex: https://dominio.com/avaliacoes/12/pdf)
    """
    numero = avaliacao.get("whatsapp_aluno")
    nome = avaliacao.get("nome_aluno", "Aluno")

    if not numero:
        return {
            "success": False,
            "status": 403,
            "message": "WhatsApp do aluno não encontrado"
        }

    mensagem = (
        f"Olá {nome}, segue o link para a sua avaliação física:\n\n"
        f"{url_pdf}\n\n"
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

        registrar_log_envio(avaliacao["id_aluno"], "whatsapp", numero, mensagem, "sucesso")

        return {
            "success": True,
            "status": 200,
            "message": "Avaliação enviada com sucesso via WhatsApp"
        }

    except Exception as e:
        print("[WhatsApp] Erro ao enviar:", e)
        registrar_log_envio(
            avaliacao["id_aluno"],
            "whatsapp",
            numero,
            f"Erro no envio WhatsApp: {mensagem}",
            f"falha: {str(e)}"
        )
        return {
            "success": False,
            "status": 500,
            "message": f"Erro ao enviar via WhatsApp: {str(e)}"
        }
