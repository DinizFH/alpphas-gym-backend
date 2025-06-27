import { useState } from "react";
import api from "../../axios";

export default function ModalCriarExercicio({ visivel, onFechar, onSalvar }) {
  const [nome, setNome] = useState("");
  const [grupoMuscular, setGrupoMuscular] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [video, setVideo] = useState("");
  const [carregando, setCarregando] = useState(false);

  if (!visivel) return null;

  const handleSalvar = async () => {
    if (!nome || !grupoMuscular) {
      alert("Preencha os campos obrigatórios.");
      return;
    }

    setCarregando(true);

    try {
      const response = await api.post("/exercicios", {
        nome,
        grupo_muscular: grupoMuscular,
        observacoes,
        video,
      });

      const novoExercicio = response.data;
      onSalvar(novoExercicio);
      onFechar();
    } catch (error) {
      console.error("Erro ao criar exercício:", error);
      alert("Erro ao criar exercício.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
        <h2 className="text-xl font-semibold mb-4">Criar Novo Exercício</h2>

        <div className="flex flex-col gap-3">
          <div>
            <label htmlFor="nome" className="block text-sm font-medium">Nome do exercício*</label>
            <input
              id="nome"
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="border px-3 py-2 rounded w-full"
            />
          </div>

          <div>
            <label htmlFor="grupoMuscular" className="block text-sm font-medium">Grupo muscular*</label>
            <input
              id="grupoMuscular"
              type="text"
              value={grupoMuscular}
              onChange={(e) => setGrupoMuscular(e.target.value)}
              className="border px-3 py-2 rounded w-full"
            />
          </div>

          <div>
            <label htmlFor="observacoes" className="block text-sm font-medium">Observações</label>
            <textarea
              id="observacoes"
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              className="border px-3 py-2 rounded w-full"
            />
          </div>

          <div>
            <label htmlFor="video" className="block text-sm font-medium">Link do vídeo (opcional)</label>
            <input
              id="video"
              type="text"
              value={video}
              onChange={(e) => setVideo(e.target.value)}
              className="border px-3 py-2 rounded w-full"
            />
          </div>
        </div>

        <div className="flex justify-end mt-6 gap-4">
          <button
            onClick={onFechar}
            className="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Cancelar
          </button>
          <button
            onClick={handleSalvar}
            disabled={carregando}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            {carregando ? "Salvando..." : "Salvar e Adicionar"}
          </button>
        </div>
      </div>
    </div>
  );
}
