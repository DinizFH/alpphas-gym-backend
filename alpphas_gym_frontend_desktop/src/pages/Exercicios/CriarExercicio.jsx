import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function CriarExercicio() {
  const [nome, setNome] = useState("");
  const [grupoMuscular, setGrupoMuscular] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [video, setVideo] = useState("");
  const navigate = useNavigate();

  const tipoUsuario = localStorage.getItem("perfil_tipo");

  if (tipoUsuario !== "personal") {
    return <Layout><p className="p-6 text-red-600">Acesso não autorizado.</p></Layout>;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!nome || !grupoMuscular) {
      alert("Preencha todos os campos obrigatórios.");
      return;
    }

    try {
      await api.post("/exercicios", {
        nome,
        grupo_muscular: grupoMuscular,
        observacoes,
        video
      });

      alert("Exercício criado com sucesso!");
      navigate("/exercicios");
    } catch (error) {
      console.error("Erro ao criar exercício:", error);
      alert("Erro ao criar exercício.");
    }
  };

  return (
    <Layout>
      <div className="p-6 max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Criar Exercício</h1>
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
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Salvar Exercício
          </button>
        </form>
      </div>
    </Layout>
  );
}
