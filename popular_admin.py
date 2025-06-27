# popular_admin.py

import os
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()  # carrega variáveis do .env se estiver usando

# Dados do admin
nome = "Administrador"
email = "administrador@alpphasgym.com"
senha = "@lpphasGym_#sistema"
senha_hash = generate_password_hash(senha)
tipo = "admin"

# Configurar conexão (ajuste se necessário)
db = pymysql.connect(
    host="localhost",
    user="root",
    password="Diniz@3582",
    database="alpphas_gym_test",  # ou alpphas_gym
    port=3307,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with db.cursor() as cursor:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            print("⚠️  Admin já existe no banco.")
        else:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, ativo)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (nome, email, senha_hash, tipo))
            db.commit()
            print("✅ Admin criado com sucesso!")
finally:
    db.close()
