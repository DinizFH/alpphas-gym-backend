import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function TreinosScreen() {
  const [usuario, setUsuario] = useState(null);
  const [busca, setBusca] = useState("");
  const [resultados, setResultados] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchPerfil() {
      try {
        const res = await api.get("/usuarios/perfil");
        setUsuario(res.data);
        if (res.data.tipo_usuario === "personal") {
          fetchTreinos();
        }
      } catch (err) {
        console.error("Erro ao carregar perfil:", err);
      }
    }
    fetchPerfil();
  }, []);

  async function fetchTreinos(nome = "") {
    try {
      const res = await api.get(`/treinos/profissional?nome=${nome}`);
      setResultados(res.data);
    } catch (err) {
      console.error("Erro ao buscar treinos:", err);
    }
  }

  const handleExcluir = async (id_treino) => {
    if (!window.confirm("Deseja realmente excluir este treino?")) return;
    try {
      await api.delete(`/treinos/${id_treino}`);
      fetchTreinos();
    } catch (err) {
      console.error("Erro ao excluir treino:", err);
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Treinos</h1>
          {usuario?.tipo_usuario === "personal" && (
            <button
              onClick={() => navigate("/treinos/novo")}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Novo Treino
            </button>
          )}
        </div>

        <input
          type="text"
          placeholder="Buscar aluno por nome..."
          className="w-full border px-3 py-2 rounded mb-4"
          value={busca}
          onChange={(e) => {
            setBusca(e.target.value);
            fetchTreinos(e.target.value);
          }}
        />

        {resultados.length === 0 ? (
          <p className="text-gray-500">Nenhum aluno com treino encontrado.</p>
        ) : (
          <div className="space-y-6">
            {resultados.map((aluno) => (
              <div key={aluno.id_usuario} className="bg-white p-4 rounded shadow">
                <div className="mb-2">
                  <p className="font-semibold text-lg">{aluno.nome}</p>
                  <p className="text-sm text-gray-600">CPF: {aluno.cpf}</p>
                </div>
                <ul className="list-disc ml-5 text-sm text-gray-800">
                  {aluno.treinos.map((treino) => (
                    <li key={treino.id_treino} className="flex justify-between items-center py-2">
                      <span>{treino.nome_treino}</span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => navigate(`/treinos/${treino.id_treino}`)}
                          className="bg-gray-200 text-black px-3 py-1 rounded hover:bg-gray-300 text-sm"
                        >
                          Detalhes
                        </button>
                        {usuario?.tipo_usuario === "personal" && (
                          <>
                            <button
                              onClick={() => navigate(`/treinos/${treino.id_treino}/editar`)}
                              className="bg-yellow-400 text-black px-3 py-1 rounded hover:bg-yellow-500 text-sm"
                            >
                              Editar
                            </button>
                            <button
                              onClick={() => handleExcluir(treino.id_treino)}
                              className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-sm"
                            >
                              Excluir
                            </button>
                          </>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
