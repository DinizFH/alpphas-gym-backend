import os
from flask_mail import Message
from app.extensions.mail import mail
from app.utils.logs import registrar_log_envio

def enviar_avaliacao_por_email(avaliacao, pdf_buffer):
    """
    Envia a avaliação física por e-mail com o PDF anexado.

    Parâmetros:
    - avaliacao: dict retornado por detalhar_avaliacao_para_uso
    - pdf_buffer: BytesIO do PDF gerado (usado com send_file ou geração interna)
    """
    email_destino = avaliacao.get("email_aluno")
    nome_destino = avaliacao.get("nome_aluno", "Aluno")
    nome_profissional = avaliacao.get("nome_profissional", "Profissional")

    if not email_destino:
        return {
            "success": False,
            "status": 400,
            "message": "E-mail do aluno não encontrado"
        }

    try:
        msg = Message(
            subject="Sua Avaliação Física - Alpphas GYM",
            recipients=[email_destino],
            body=(
                f"Olá {nome_destino},\n\n"
                f"Segue em anexo a sua avaliação física, realizada por {nome_profissional}.\n\n"
                f"Em caso de dúvidas, estamos à disposição!\n\n"
                f"Equipe Alpphas GYM"
            )
        )

        msg.attach(
            filename="avaliacao_fisica.pdf",
            content_type="application/pdf",
            data=pdf_buffer.getvalue()
        )

        mail.send(msg)

        registrar_log_envio(avaliacao["id_aluno"], "email", email_destino, "PDF da avaliação enviado", "sucesso")

        return {
            "success": True,
            "status": 200,
            "message": "Avaliação enviada com sucesso por e-mail"
        }

    except Exception as e:
        print("[E-MAIL] Erro ao enviar:", e)
        registrar_log_envio(
            avaliacao["id_aluno"],
            "email",
            email_destino,
            f"Erro no envio do PDF da avaliação",
            f"falha: {str(e)}"
        )
        return {
            "success": False,
            "status": 500,
            "message": f"Erro ao enviar por e-mail: {str(e)}"
        }
