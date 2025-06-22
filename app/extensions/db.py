import pymysql
from flask import current_app

def get_db():
    config = current_app.config.get('DB_CONFIG', {})
    try:
        conn = pymysql.connect(
            host=config.get('host', 'localhost'),
            user=config.get('user', 'root'),
            password=config.get('password', ''),
            database=config.get('database', ''),
            port=int(config.get('port', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        db_name = config.get('database', 'desconhecido')
        print(f"[ERRO] Falha ao conectar ao banco '{db_name}': {e}")
        raise RuntimeError(f"Erro ao conectar ao banco de dados '{db_name}'. Verifique a configuração e se o banco está acessível.")
