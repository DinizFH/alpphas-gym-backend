from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
import os

def gerar_pdf_avaliacao(avaliacao, nome_arquivo="avaliacao_temp.pdf", salvar_em_disco=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marca d'água com logo central e transparente
    try:
        logo_path = "app/static/img/alpphas_logo.png"
        watermark = ImageReader(logo_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))  # Transparente
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
    c.drawString(80, y, f"Aluno: {avaliacao['nome_aluno']}")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(80, y, f"Data: {avaliacao['data']}")
    y -= 20

    # Medidas corporais
    c.setFont("Helvetica", 10)
    for nome, valor in avaliacao["medidas"].items():
        if valor is not None:
            nome_formatado = nome.replace("_", " ").capitalize()
            c.drawString(80, y, f"{nome_formatado}: {valor}")
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 80

    # Observações
    if avaliacao.get("observacoes"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y, "Observações:")
        y -= 15
        c.setFont("Helvetica", 10)
        for linha in avaliacao["observacoes"].splitlines():
            c.drawString(90, y, linha)
            y -= 13
            if y < 100:
                c.showPage()
                y = height - 80

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
