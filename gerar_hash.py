from werkzeug.security import generate_password_hash

usuarios = {
    "aluno": generate_password_hash("123456"),
    "personal": generate_password_hash("123456"),
    "nutricionista": generate_password_hash("123456")
}

for tipo, hash_gerado in usuarios.items():
from werkzeug.security import generate_password_hash

usuarios = {
    "aluno": generate_password_hash("123456"),
    "personal": generate_password_hash("123456"),
    "nutricionista": generate_password_hash("123456")
}

for tipo, hash_gerado in usuarios.items():
    print(f"{tipo}: {hash_gerado}")