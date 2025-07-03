import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from matplotlib import pyplot as plt
from datetime import datetime

def gerar_pdf_avaliacao(avaliacao, historico=[]):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(2 * cm, altura - 2 * cm, "Relatório de Avaliação Física")

    # Dados principais
    pdf.setFont("Helvetica", 12)
    pdf.drawString(2 * cm, altura - 3.5 * cm, f"Aluno: {avaliacao['nome_aluno']}")
    pdf.drawString(2 * cm, altura - 4.2 * cm, f"Profissional: {avaliacao['nome_profissional']}")
    data_formatada = datetime.strptime(avaliacao["data_avaliacao"], "%Y-%m-%d").strftime("%d/%m/%Y")
    pdf.drawString(2 * cm, altura - 4.9 * cm, f"Data da Avaliação: {data_formatada}")

    # Dados físicos
    pdf.drawString(2 * cm, altura - 6 * cm, f"Peso: {avaliacao['peso']} kg")
    pdf.drawString(8 * cm, altura - 6 * cm, f"Altura: {avaliacao['altura']} cm")
    pdf.drawString(2 * cm, altura - 6.7 * cm, f"Percentual de Gordura: {avaliacao['percentual_gordura']}%")
    pdf.drawString(8 * cm, altura - 6.7 * cm, f"Massa Magra: {avaliacao['massa_magra']} kg")

    # Dobras cutâneas
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(2 * cm, altura - 8 * cm, "Dobras Cutâneas (mm):")
    pdf.setFont("Helvetica", 11)

    y = altura - 8.8 * cm
    for campo, label in {
        "dobra_triceps": "Tríceps",
        "dobra_subescapular": "Subescapular",
        "dobra_biceps": "Bíceps",
        "dobra_axilar_media": "Axilar Média",
        "dobra_supra_iliaca": "Supra Ilíaca"
    }.items():
        valor = avaliacao.get(campo)
        if valor is not None:
            pdf.drawString(2 * cm, y, f"{label}: {valor} mm")
            y -= 0.6 * cm

    # Gráfico evolução massa magra vs gordura
    if historico and len(historico) >= 2:
        datas = [datetime.strptime(a["data_avaliacao"], "%Y-%m-%d").strftime("%d/%m") for a in historico]
        magra = [a["massa_magra"] for a in historico]
        gorda = [a["massa_gorda"] for a in historico]

        plt.figure(figsize=(6, 3))
        plt.plot(datas, magra, label="Massa Magra", marker='o')
        plt.plot(datas, gorda, label="Massa Gorda", marker='o')
        plt.xlabel("Data")
        plt.ylabel("Kg")
        plt.title("Evolução da Composição Corporal")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="PNG")
        img_buffer.seek(0)
        imagem = ImageReader(img_buffer)
        pdf.drawImage(imagem, 2 * cm, 2 * cm, width=16 * cm, height=7 * cm)
        plt.close()

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
