import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

def gerar_pdf_avaliacao(avaliacao, nome_arquivo="avaliacao_temp.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marca d'água com logo central transparente
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        watermark = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))
        c.drawImage(watermark, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()
    except Exception as e:
        print(f"Erro ao carregar logo transparente: {e}")

    # Cabeçalho com logo no canto superior esquerdo
    try:
        c.drawImage(logo_path, 40, height - 80, width=60, height=60, mask='auto')
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    # Dados do profissional
    c.setFont("Helvetica", 10)
    x_dados = 120
    y_dados = height - 50
    c.drawString(x_dados, y_dados, f"Profissional: {avaliacao['nome_profissional']}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"Telefone: {avaliacao.get('telefone') or 'Não informado'}")
    y_dados -= 15
    c.drawString(x_dados, y_dados, f"E-mail: {avaliacao.get('email') or 'Não informado'}")
    y_dados -= 15
    if avaliacao.get("cref"):
        c.drawString(x_dados, y_dados, f"CREF: {avaliacao['cref']}")
    elif avaliacao.get("crn"):
        c.drawString(x_dados, y_dados, f"CRN: {avaliacao['crn']}")

    # Linha horizontal
    linha_y = y_dados - 10
    c.setLineWidth(1)
    c.line(40, linha_y, width - 40, linha_y)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, linha_y - 30, "Avaliação Física")

    # Dados do aluno
    y = linha_y - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, f"Aluno: {avaliacao['nome_aluno']}")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Data da Avaliação: {avaliacao['data_avaliacao_formatada']}")
    y -= 20
    c.drawString(60, y, f"Peso: {avaliacao.get('peso', '---')} kg")
    y -= 20
    c.drawString(60, y, f"Altura: {avaliacao.get('altura', '---')} m")
    y -= 20
    c.drawString(60, y, f"IMC: {avaliacao.get('imc', '---')}")
    y -= 20
    c.drawString(60, y, f"% Gordura Corporal: {avaliacao.get('percentual_gordura', '---')}%")
    y -= 30

    # Dobras Cutâneas
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, "Dobras Cutâneas:")
    y -= 20
    c.setFont("Helvetica", 11)
    dobras = [
        "dobra_triceps", "dobra_subescapular", "dobra_biceps",
        "dobra_axilar_media", "dobra_supra_iliaca"
    ]
    for d in dobras:
        valor = avaliacao.get(d)
        if valor is not None:
            c.drawString(80, y, f"{d.replace('_', ' ').title()}: {valor} mm")
            y -= 15

    y -= 20

    # Medidas Corporais
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, "Medidas Corporais:")
    y -= 20
    c.setFont("Helvetica", 11)
    medidas = [
        ("Cintura", "cintura"),
        ("Quadril", "quadril"),
        ("Peitoral", "peitoral"),
        ("Abdômen", "abdomen"),
        ("Coxa Direita", "coxa_d"),
        ("Coxa Esquerda", "coxa_e"),
        ("Braço D Contraído", "braco_d_contraido"),
        ("Braço E Contraído", "braco_e_contraido")
    ]
    for nome, chave in medidas:
        valor = avaliacao.get(chave)
        if valor is not None:
            c.drawString(80, y, f"{nome}: {valor} cm")
            y -= 15

    c.save()
    buffer.seek(0)

    if salvar_em_disco:
        caminho = os.path.join("app", "static", "pdfs", nome_arquivo)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "wb") as f:
            f.write(buffer.getbuffer())
        return caminho
    else:
        return buffer
