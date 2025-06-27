import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function EditarExercicio() {
  const { id } = useParams();
  const navigate = useNavigate();
  const tipoUsuario = localStorage.getItem("perfil_tipo");

  const [nome, setNome] = useState("");
  const [grupoMuscular, setGrupoMuscular] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [video, setVideo] = useState("");

  useEffect(() => {
    buscarExercicio();
  }, []);

  const buscarExercicio = async () => {
    try {
      const response = await api.get(`/exercicios/${id}`);
      const exercicio = response.data;
      setNome(exercicio.nome);
      setGrupoMuscular(exercicio.grupo_muscular);
      setObservacoes(exercicio.observacoes);
      setVideo(exercicio.video);
    } catch (error) {
      console.error("Erro ao buscar exercício:", error);
      alert("Erro ao buscar dados do exercício.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!nome || !grupoMuscular) {
      alert("Preencha todos os campos obrigatórios.");
      return;
    }

    try {
      await api.put(`/exercicios/${id}`, {
        nome,
        grupo_muscular: grupoMuscular,
        observacoes,
        video,
      });

      alert("Exercício atualizado com sucesso!");
      navigate("/exercicios");
    } catch (error) {
      console.error("Erro ao atualizar exercício:", error);
      alert("Erro ao atualizar exercício.");
    }
  };

  if (tipoUsuario !== "personal") {
    return (
      <Layout>
        <p className="p-6 text-red-600">Acesso não autorizado.</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Editar Exercício</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Nome do exercício*"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            className="border px-3 py-2 rounded"
          />
          <input
            type="text"
            placeholder="Grupo muscular*"
            value={grupoMuscular}
            onChange={(e) => setGrupoMuscular(e.target.value)}
            className="border px-3 py-2 rounded"
          />
          <textarea
            placeholder="Observações"
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            className="border px-3 py-2 rounded"
          />
          <input
            type="text"
            placeholder="Link do vídeo (opcional)"
            value={video}
            onChange={(e) => setVideo(e.target.value)}
            className="border px-3 py-2 rounded"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Atualizar Exercício
          </button>
        </form>
      </div>
    </Layout>
  );
}
