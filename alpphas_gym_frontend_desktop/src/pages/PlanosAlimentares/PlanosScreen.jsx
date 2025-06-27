import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import ModalSelecionarAluno from "./ModalSelecionarAluno";
import ModalConfirmarExclusao from "./ModalConfirmarExclusao";
import ModalEnviarPlano from "./ModalEnviarPlano";

export default function PlanosScreen() {
  const [planos, setPlanos] = useState([]);
  const [filtro, setFiltro] = useState("");
  const [tipo, setTipo] = useState("");
  const [mostrarModal, setMostrarModal] = useState(false);
  const [mostrarModalExclusao, setMostrarModalExclusao] = useState(false);
  const [mostrarModalEnviar, setMostrarModalEnviar] = useState(false);
  const [planoSelecionado, setPlanoSelecionado] = useState(null);
  const navigate = useNavigate();

  const carregarPlanos = async () => {
    try {
      const perfil = await api.get("/usuarios/perfil");
      setTipo(perfil.data.tipo_usuario);

      const resposta = await api.get("/planos/");
      setPlanos(resposta.data);
    } catch (err) {
      console.error("Erro ao carregar planos:", err);
    }
  };

  useEffect(() => {
    carregarPlanos();
  }, []);

  const handleCriarPlano = () => {
    setMostrarModal(true);
  };

  const handleVerDetalhes = (id) => {
    navigate(`/planos/${id}`);
  };

  const handleEditar = (id) => {
    navigate(`/planos/${id}/editar`);
  };

  const confirmarExclusao = (plano) => {
    setPlanoSelecionado(plano);
    setMostrarModalExclusao(true);
  };

  const handleExcluir = async () => {
    try {
      await api.delete(`/planos/${planoSelecionado.id_plano}`);
      setPlanos(planos.filter((p) => p.id_plano !== planoSelecionado.id_plano));
      setMostrarModalExclusao(false);
    } catch (err) {
      console.error("Erro ao excluir plano:", err);
      alert("Erro ao excluir plano.");
    }
  };

  const abrirModalEnviar = (plano) => {
    setPlanoSelecionado(plano);
    setMostrarModalEnviar(true);
  };

  const handleExportarPDF = async (id) => {
    try {
      const response = await api.get(`/planos/${id}/pdf`, {
        responseType: "blob",
      });

      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `plano_alimentar_${id}.pdf`;
      link.click();
    } catch (err) {
      alert("Erro ao gerar PDF.");
    }
  };

  const formatarData = (dataISO) => {
    const d = new Date(dataISO);
    return d.toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const planosFiltrados = planos.filter((plano) => {
    const termo = filtro.toLowerCase();
    return plano.nome_aluno?.toLowerCase().includes(termo);
  });

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Planos Alimentares</h1>
          {tipo === "nutricionista" && (
            <button
              onClick={handleCriarPlano}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              + Criar Plano
            </button>
          )}
        </div>

        <input
          type="text"
          placeholder="Buscar por nome do aluno..."
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
          className="w-full p-2 mb-6 border rounded"
        />

        <div className="grid gap-4">
          {planosFiltrados.length === 0 ? (
            <p className="text-gray-500">Nenhum plano encontrado.</p>
          ) : (
            planosFiltrados.map((plano) => (
              <div key={plano.id_plano} className="bg-white shadow p-4 rounded">
                <div className="flex justify-between items-center">
                  <div className="space-y-1">
                    <p><strong>Aluno:</strong> {plano.nome_aluno}</p>
                    <p><strong>Nutricionista:</strong> {plano.nome_profissional}</p>
                    {plano.data_criacao && (
                      <p><strong>Data:</strong> {formatarData(plano.data_criacao)}</p>
                    )}
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <button
                      className="text-blue-600 underline"
                      onClick={() => handleVerDetalhes(plano.id_plano)}
                    >
                      Ver Detalhes
                    </button>

                    <button
                      className="text-purple-600 underline"
                      onClick={() => handleExportarPDF(plano.id_plano)}
                    >
                      Exportar
                    </button>

                    {tipo === "nutricionista" && (
                      <>
                        <button
                          className="text-yellow-600 underline"
                          onClick={() => handleEditar(plano.id_plano)}
                        >
                          Editar
                        </button>
                        <button
                          className="text-red-600 underline"
                          onClick={() => confirmarExclusao(plano)}
                        >
                          Excluir
                        </button>
                        <button
                          className="text-green-600 underline"
                          onClick={() => abrirModalEnviar(plano)}
                        >
                          Enviar
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {mostrarModal && (
        <ModalSelecionarAluno
          onClose={() => setMostrarModal(false)}
          onPlanoCriado={carregarPlanos}
        />
      )}

      {mostrarModalExclusao && planoSelecionado && (
        <ModalConfirmarExclusao
          nomePlano={`Plano de ${planoSelecionado.nome_aluno}`}
          onClose={() => setMostrarModalExclusao(false)}
          onConfirm={handleExcluir}
        />
      )}

      {mostrarModalEnviar && planoSelecionado && (
        <ModalEnviarPlano
          idPlano={planoSelecionado.id_plano}
          onClose={() => setMostrarModalEnviar(false)}
        />
      )}
    </Layout>
  );
}
