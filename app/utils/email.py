# app/utils/email.py
import os
from flask_mail import Message
from flask import current_app
from app.extensions.mail import mail

def enviar_email_com_anexo(destinatario, assunto, corpo, caminho_anexo):
    try:
        msg = Message(
            subject=assunto,
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[destinatario],
            body=corpo,
        )

        with open(caminho_anexo, "rb") as fp:
            msg.attach(
                filename=os.path.basename(caminho_anexo),
                content_type="application/pdf",
                data=fp.read()
            )

        mail.send(msg)
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail: {e}")
        return False

