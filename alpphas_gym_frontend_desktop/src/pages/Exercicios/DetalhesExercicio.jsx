import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function DetalhesExercicio() {
  const { id } = useParams();
  const navigate = useNavigate();
  const tipoUsuario = localStorage.getItem("perfil_tipo");

  const [exercicio, setExercicio] = useState(null);

  useEffect(() => {
    buscarExercicio();
  }, []);

  const buscarExercicio = async () => {
    try {
      const response = await api.get(`/exercicios/${id}`);
      setExercicio(response.data);
    } catch (error) {
      console.error("Erro ao buscar exercício:", error);
      alert("Erro ao carregar dados do exercício.");
    }
  };

  const excluirExercicio = async () => {
    if (!window.confirm("Deseja realmente excluir este exercício?")) return;
    try {
      await api.delete(`/exercicios/${id}`);
      alert("Exercício excluído com sucesso!");
      navigate("/exercicios");
    } catch (error) {
      console.error("Erro ao excluir exercício:", error);
      alert("Erro ao excluir exercício.");
    }
  };

  if (!exercicio) {
    return (
      <Layout>
        <p className="p-6">Carregando...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">{exercicio.nome}</h1>
        <p className="text-gray-700 mb-1">
          <strong>Grupo Muscular:</strong> {exercicio.grupo_muscular}
        </p>
        <p className="text-gray-700 mb-1">
          <strong>Observações:</strong>{" "}
          {exercicio.observacoes ? exercicio.observacoes : "Nenhuma"}
        </p>
        {exercicio.video && (
          <p className="text-blue-600 mb-4">
            <a href={exercicio.video} target="_blank" rel="noreferrer">
              Ver vídeo do exercício
            </a>
          </p>
        )}

        {tipoUsuario === "personal" && (
          <div className="flex gap-4 mt-4">
            <Link
              to={`/exercicios/editar/${id}`}
              className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
            >
              Editar
            </Link>
            <button
              onClick={excluirExercicio}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Excluir
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
