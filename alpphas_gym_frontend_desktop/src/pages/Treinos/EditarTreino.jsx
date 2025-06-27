import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import ModalCriarExercicio from "../../pages/Exercicios/ModalCriarExercicio";

export default function EditarTreino() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [treino, setTreino] = useState(null);
  const [nomeTreino, setNomeTreino] = useState("");
  const [exercicios, setExercicios] = useState([]);
  const [formExercicio, setFormExercicio] = useState({ series: "", repeticoes: "", observacoes: "" });
  const [novoExercicio, setNovoExercicio] = useState("");
  const [resultadosExercicio, setResultadosExercicio] = useState([]);
  const [exercicioSelecionado, setExercicioSelecionado] = useState(null);
  const [modalVisivel, setModalVisivel] = useState(false);

  useEffect(() => {
    async function fetchTreino() {
      try {
        const res = await api.get(`/treinos/${id}`);
        setTreino(res.data);
        setNomeTreino(res.data.nome_treino);
        setExercicios(res.data.exercicios);
      } catch (err) {
        console.error("Erro ao carregar treino:", err);
      }
    }
    fetchTreino();
  }, [id]);

  useEffect(() => {
    if (novoExercicio.length >= 2) {
      const delay = setTimeout(async () => {
        const res = await api.get(`/exercicios?nome=${novoExercicio}`);
        setResultadosExercicio(res.data);
      }, 300);
      return () => clearTimeout(delay);
    } else {
      setResultadosExercicio([]);
    }
  }, [novoExercicio]);

  const adicionarExercicioAoTreino = () => {
    setExercicios([...exercicios, {
      ...exercicioSelecionado,
      nome_exercicio: exercicioSelecionado.nome_exercicio || exercicioSelecionado.nome,
      series: formExercicio.series,
      repeticoes: formExercicio.repeticoes,
      observacoes: formExercicio.observacoes
    }]);
    setExercicioSelecionado(null);
    setNovoExercicio("");
    setFormExercicio({ series: "", repeticoes: "", observacoes: "" });
    setResultadosExercicio([]);
  };

  const removerExercicio = (index) => {
    const novaLista = [...exercicios];
    novaLista.splice(index, 1);
    setExercicios(novaLista);
  };

  const handleSalvar = async () => {
    try {
      await api.put(`/treinos/${id}`, {
        nome_treino: nomeTreino,
        exercicios: exercicios.map(e => ({
          id_exercicio: e.id_exercicio,
          series: e.series,
          repeticoes: e.repeticoes,
          observacoes: e.observacoes
        }))
      });
      navigate("/treinos");
    } catch (err) {
      console.error("Erro ao salvar treino:", err);
    }
  };

  const handleSalvarExercicioModal = (novoExercicioCriado) => {
    setExercicioSelecionado({
      ...novoExercicioCriado,
      nome_exercicio: novoExercicioCriado.nome
    });
  };

  if (!treino) return <Layout><div className="p-6">Carregando...</div></Layout>;

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Editar Treino</h1>

        <div className="mb-4">
          <label className="block mb-1 font-medium">Nome do Treino</label>
          <input
            type="text"
            value={nomeTreino}
            onChange={(e) => setNomeTreino(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Adicionar Exercício</label>
          <input
            type="text"
            placeholder="Buscar exercício..."
            value={novoExercicio}
            onChange={(e) => setNovoExercicio(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          />

          <ul className="border mt-1 rounded max-h-40 overflow-y-auto">
            {resultadosExercicio.map((ex) => (
              <li
                key={ex.id_exercicio}
                className="p-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => {
                  setExercicioSelecionado({
                    ...ex,
                    nome_exercicio: ex.nome
                  });
                  setResultadosExercicio([]);
                }}
              >
                {ex.nome}
              </li>
            ))}
          </ul>

          {resultadosExercicio.length === 0 && novoExercicio.length > 2 && (
            <p className="text-sm text-gray-500 mt-2">
              Nenhum exercício encontrado.
              <button
                onClick={() => setModalVisivel(true)}
                className="ml-2 text-blue-600 underline"
              >
                Criar novo exercício
              </button>
            </p>
          )}

          {exercicioSelecionado && (
            <>
              <p className="mt-4 text-sm">
                <strong>Selecionado:</strong> {exercicioSelecionado.nome_exercicio}
              </p>
              <div className="grid grid-cols-3 gap-2 mt-2">
                <div>
                  <label className="block text-sm">Séries</label>
                  <input
                    type="text"
                    placeholder="Séries"
                    value={formExercicio.series}
                    onChange={(e) => setFormExercicio({ ...formExercicio, series: e.target.value })}
                    className="border px-2 py-1 rounded w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm">Repetições</label>
                  <input
                    type="text"
                    placeholder="Repetições"
                    value={formExercicio.repeticoes}
                    onChange={(e) => setFormExercicio({ ...formExercicio, repeticoes: e.target.value })}
                    className="border px-2 py-1 rounded w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm">Observações</label>
                  <input
                    type="text"
                    placeholder="Observações"
                    value={formExercicio.observacoes}
                    onChange={(e) => setFormExercicio({ ...formExercicio, observacoes: e.target.value })}
                    className="border px-2 py-1 rounded w-full"
                  />
                </div>
              </div>
              <button
                onClick={adicionarExercicioAoTreino}
                className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
              >
                Adicionar ao Treino
              </button>
            </>
          )}
        </div>

        <div className="mt-6">
          <h3 className="font-semibold">Exercícios no treino:</h3>
          <ul className="list-disc ml-6">
            {exercicios.map((e, i) => (
              <li key={i} className="flex items-center justify-between">
                <span>
                  {e.nome_exercicio || e.nome} - {e.series}x{e.repeticoes} ({e.observacoes})
                </span>
                <button
                  onClick={() => removerExercicio(i)}
                  className="ml-4 text-red-600 hover:underline text-sm"
                >
                  Remover
                </button>
              </li>
            ))}
          </ul>
        </div>

        <button
          onClick={handleSalvar}
          className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
        >
          Salvar Alterações
        </button>
      </div>

      <ModalCriarExercicio
        visivel={modalVisivel}
        onFechar={() => setModalVisivel(false)}
        onSalvar={handleSalvarExercicioModal}
      />
    </Layout>
  );
}
