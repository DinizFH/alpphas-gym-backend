import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function AvaliacoesScreen() {
  const [avaliacoes, setAvaliacoes] = useState([]);
  const [tipoUsuario, setTipoUsuario] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchAvaliacoes() {
      try {
        const perfilRes = await api.get("/usuarios/perfil");
        setTipoUsuario(perfilRes.data.tipo_usuario);

        const res = await api.get("/avaliacoes/");
        setAvaliacoes(res.data);
      } catch (err) {
        console.error("Erro ao carregar avaliações:", err);
        alert("Erro ao carregar avaliações.");
      }
    }

    fetchAvaliacoes();
  }, []);

  const excluirAvaliacao = async (id_avaliacao) => {
    if (!window.confirm("Deseja realmente excluir esta avaliação?")) return;

    try {
      await api.delete(`/avaliacoes/${id_avaliacao}`);
      setAvaliacoes((prev) =>
        prev.filter((a) => a.id_avaliacao !== id_avaliacao)
      );
    } catch (err) {
      console.error("Erro ao excluir avaliação:", err);
      alert("Erro ao excluir.");
    }
  };

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Avaliações Físicas</h1>

          {(tipoUsuario === "personal" || tipoUsuario === "nutricionista") && (
            <button
              onClick={() => navigate("/avaliacoes/nova")}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Nova Avaliação
            </button>
          )}
        </div>

        {avaliacoes.length === 0 ? (
          <p className="text-gray-600">Nenhuma avaliação encontrada.</p>
        ) : (
          <div className="grid gap-4">
            {avaliacoes.map((avaliacao) => (
              <div
                key={avaliacao.id_avaliacao}
                className="bg-white p-4 rounded shadow flex flex-col sm:flex-row justify-between items-start sm:items-center"
              >
                <div>
                  <p className="font-semibold">
                    Aluno: {avaliacao.nome_aluno || "Desconhecido"}
                  </p>
                  {tipoUsuario !== "aluno" && (
                    <p className="text-sm text-gray-600">
                      CPF: {avaliacao.cpf_aluno || "Não informado"}
                    </p>
                  )}
                  <p className="text-sm text-gray-600">
                    Profissional: {avaliacao.nome_profissional || "Desconhecido"}
                  </p>
                  <p className="text-sm text-gray-600">
                    Data:{" "}
                    {avaliacao.data_avaliacao
                      ? new Date(avaliacao.data_avaliacao).toLocaleDateString()
                      : "Não informada"}
                  </p>
                </div>

                <div className="flex gap-2 mt-4 sm:mt-0">
                  <button
                    onClick={() =>
                      navigate(`/avaliacoes/${avaliacao.id_avaliacao}`)
                    }
                    className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm"
                  >
                    Detalhes
                  </button>

                  {(tipoUsuario === "personal" || tipoUsuario === "nutricionista") && (
                    <>
                      <button
                        onClick={() =>
                          navigate(`/avaliacoes/${avaliacao.id_avaliacao}/editar`)
                        }
                        className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-sm"
                      >
                        Editar
                      </button>

                      <button
                        onClick={() => excluirAvaliacao(avaliacao.id_avaliacao)}
                        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                      >
                        Excluir
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
