import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import ModalEnviarPlano from "./ModalEnviarPlano";

export default function VerPlanoAlimentar() {
  const { id } = useParams();
  const [plano, setPlano] = useState(null);
  const [tipo, setTipo] = useState("");
  const [mostrarModal, setMostrarModal] = useState(false);

  useEffect(() => {
    async function carregarDados() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setTipo(perfil.data.tipo_usuario);

        const res = await api.get(`/planos/${id}`);
        setPlano(res.data);
      } catch (err) {
        console.error("Erro ao carregar plano:", err);
        alert("Erro ao carregar plano alimentar.");
      }
    }

    carregarDados();
  }, [id]);

  const handleExportarPDF = async () => {
    try {
      const response = await api.get(`/planos/${id}/pdf`, {
        responseType: "blob",
      });

      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = "plano_alimentar.pdf";
      link.click();
    } catch (err) {
      console.error("Erro ao exportar PDF:", err);
      alert("Erro ao gerar PDF");
    }
  };

  if (!plano) {
    return (
      <Layout>
        <div className="p-6">Carregando plano alimentar...</div>
      </Layout>
    );
  }

  const formatarData = (dataISO) => {
    const d = new Date(dataISO);
    return d.toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // 🔎 Limpa alimentos com nome/peso vazio e remove duplicatas
  const refeicoesLimpas = plano.refeicoes.map((ref) => {
    const alimentosValidos = ref.alimentos
      .filter((a) => a.nome?.trim() && a.peso?.toString().trim())
      .filter(
        (a, i, self) =>
          i ===
          self.findIndex(
            (b) =>
              b.nome.trim().toLowerCase() === a.nome.trim().toLowerCase() &&
              b.peso.trim() === a.peso.trim()
          )
      );

    return { ...ref, alimentos: alimentosValidos };
  });

  return (
    <Layout>
      <div className="p-6 max-w-4xl mx-auto bg-white rounded shadow">
        <h1 className="text-2xl font-bold mb-4">Plano Alimentar</h1>

        <div className="mb-4 text-sm text-gray-700 space-y-1">
          <p><strong>Aluno:</strong> {plano.nome_aluno}</p>
          <p><strong>Nutricionista:</strong> {plano.nome_profissional}</p>
          {plano.data_criacao && (
            <p><strong>Data de Criação:</strong> {formatarData(plano.data_criacao)}</p>
          )}
          {plano.titulo_refeicao && (
            <p><strong>Primeira Refeição:</strong> {plano.titulo_refeicao}</p>
          )}
        </div>

        <div className="space-y-6">
          {refeicoesLimpas.length === 0 ? (
            <p className="text-gray-500">Nenhuma refeição cadastrada para este plano.</p>
          ) : (
            refeicoesLimpas.map((ref, index) => (
              <div key={index} className="border border-gray-200 p-4 rounded bg-gray-50">
                <h2 className="text-lg font-semibold mb-1">{ref.titulo}</h2>
                <p className="text-gray-600 mb-2">
                  Calorias estimadas: <strong>{ref.calorias_estimadas || 0} kcal</strong>
                </p>
                {ref.alimentos.length > 0 ? (
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {ref.alimentos.map((alimento, i) => (
                      <li key={i}>
                        {alimento.nome} — {alimento.peso}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">Sem alimentos registrados.</p>
                )}
              </div>
            ))
          )}
        </div>

        <div className="flex flex-wrap gap-4 mt-6">
          <button
            onClick={handleExportarPDF}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Exportar PDF
          </button>

          {tipo === "nutricionista" && (
            <button
              onClick={() => setMostrarModal(true)}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              ✉️ Enviar
            </button>
          )}
        </div>

        {mostrarModal && (
          <ModalEnviarPlano idPlano={id} onClose={() => setMostrarModal(false)} />
        )}
      </div>
    </Layout>
  );
}
