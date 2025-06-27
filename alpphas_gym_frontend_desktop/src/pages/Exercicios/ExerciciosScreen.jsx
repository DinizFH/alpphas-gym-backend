import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function ExerciciosScreen() {
  const [exercicios, setExercicios] = useState([]);
  const [filtro, setFiltro] = useState("");
  const tipoUsuario = localStorage.getItem("perfil_tipo");

  useEffect(() => {
    buscarExercicios();
  }, []);

  const buscarExercicios = async () => {
    try {
      const response = await api.get("/exercicios");
      setExercicios(response.data);
    } catch (error) {
      console.error("Erro ao buscar exercícios:", error);
    }
  };

  const excluirExercicio = async (id) => {
    if (!window.confirm("Deseja realmente excluir este exercício?")) return;
    try {
      await api.delete(`/exercicios/${id}`);
      buscarExercicios();
    } catch (error) {
      console.error("Erro ao excluir exercício:", error);
    }
  };

  const exerciciosFiltrados = exercicios.filter((ex) =>
    ex.nome.toLowerCase().includes(filtro.toLowerCase())
  );

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Exercícios</h1>

        <div className="flex justify-between items-center mb-4">
          <input
            type="text"
            placeholder="Buscar por nome..."
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            className="border rounded px-3 py-1 w-1/3"
          />

          {tipoUsuario === "personal" && (
            <Link
              to="/exercicios/novo"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Criar Exercício
            </Link>
          )}
        </div>

        {exerciciosFiltrados.length === 0 ? (
          <p>Nenhum exercício encontrado.</p>
        ) : (
          <div className="grid gap-4">
            {exerciciosFiltrados.map((ex) => (
              <div key={ex.id_exercicio} className="bg-white shadow p-4 rounded-md">
                <h2 className="text-lg font-semibold">{ex.nome}</h2>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Grupo Muscular:</strong> {ex.grupo_muscular}
                </p>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Observações:</strong> {ex.observacoes || "Nenhuma"}
                </p>
                {ex.video && (
                  <p className="text-sm text-blue-600">
                    <a href={ex.video} target="_blank" rel="noreferrer">
                      Ver vídeo
                    </a>
                  </p>
                )}
                <div className="mt-2 flex gap-3">
                  <Link
                    to={`/exercicios/${ex.id_exercicio}`}
                    className="text-blue-600 hover:underline"
                  >
                    Ver detalhes
                  </Link>
                  {tipoUsuario === "personal" && (
                    <>
                      <Link
                        to={`/exercicios/editar/${ex.id_exercicio}`}
                        className="text-yellow-600 hover:underline"
                      >
                        Editar
                      </Link>
                      <button
                        onClick={() => excluirExercicio(ex.id_exercicio)}
                        className="text-red-600 hover:underline"
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
