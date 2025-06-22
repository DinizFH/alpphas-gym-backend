import json
from flask_jwt_extended import get_jwt_identity

def extrair_user_id():
    identidade = get_jwt_identity()
    if isinstance(identidade, dict):
        return identidade.get("id")
    elif isinstance(identidade, str):
        try:
            identidade = json.loads(identidade)
            return identidade.get("id")
        except:
            return None
    elif isinstance(identidade, int):
        return identidade
    return None

def extrair_user_info():
    identidade = get_jwt_identity()
    if isinstance(identidade, dict):
        return identidade
    elif isinstance(identidade, str):
        try:
            return json.loads(identidade)
        except:
            return {}
    return {}
