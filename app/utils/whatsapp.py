# app/utils/whatsapp.py

import os
import requests
from flask import current_app

def enviar_whatsapp(numero_destino, mensagem, caminho_arquivo=None):
    """
    Envia mensagem via WhatsApp usando UltraMsg.
    - Se caminho_arquivo for fornecido, envia um documento com legenda.
    - Caso contrário, envia uma mensagem de texto simples (útil para links).
    """
    try:
        instancia = current_app.config.get("ULTRAMSG_INSTANCE")
        token = current_app.config.get("ULTRAMSG_TOKEN")

        if not instancia or not token:
            raise Exception("Configuração UltraMsg ausente")

        if caminho_arquivo:
            url = f"https://api.ultramsg.com/{instancia}/messages/document"
            with open(caminho_arquivo, "rb") as file:
                response = requests.post(
                    url,
                    data={
                        "token": token,
                        "to": numero_destino,
                        "filename": os.path.basename(caminho_arquivo),
                        "caption": mensagem,
                    },
                    files={"document": file},
                )
        else:
            url = f"https://api.ultramsg.com/{instancia}/messages/chat"
            response = requests.post(
                url,
                data={
                    "token": token,
                    "to": numero_destino,
                    "body": mensagem
                }
            )

        if response.status_code == 200:
            return True
        else:
            print(f"[ERRO] Falha ao enviar WhatsApp: {response.text}")
            return False

    except Exception as e:
        print(f"[ERRO] Exceção ao enviar WhatsApp: {e}")
        return False
