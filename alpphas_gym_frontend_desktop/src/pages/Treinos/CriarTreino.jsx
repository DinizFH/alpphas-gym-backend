import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import ModalCriarExercicio from "../../pages/Exercicios/ModalCriarExercicio";

export default function CriarTreino() {
  const navigate = useNavigate();
  const [buscaAluno, setBuscaAluno] = useState("");
  const [resultadosAluno, setResultadosAluno] = useState([]);
  const [alunoSelecionado, setAlunoSelecionado] = useState(null);
  const [nomeTreino, setNomeTreino] = useState("");

  const [exercicios, setExercicios] = useState([]);
  const [exercicioSelecionado, setExercicioSelecionado] = useState(null);
  const [formExercicio, setFormExercicio] = useState({ series: "", repeticoes: "", observacoes: "" });

  const [novoExercicio, setNovoExercicio] = useState("");
  const [resultadosExercicio, setResultadosExercicio] = useState([]);
  const [modalVisivel, setModalVisivel] = useState(false);

  useEffect(() => {
    if (buscaAluno.length >= 2) {
      const delay = setTimeout(async () => {
        const res = await api.get(`/avaliacoes/buscar-aluno?nome=${buscaAluno}`);
        setResultadosAluno(res.data);
      }, 300);
      return () => clearTimeout(delay);
    }
  }, [buscaAluno]);

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
    const novos = [...exercicios];
    novos.splice(index, 1);
    setExercicios(novos);
  };

  const handleCriarTreino = async () => {
    if (!alunoSelecionado || !nomeTreino || exercicios.length === 0) return;

    try {
      await api.post("/treinos", {
        id_aluno: alunoSelecionado.id_usuario,
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
      console.error("Erro ao criar treino:", err);
    }
  };

  const handleSalvarExercicioModal = (novoExercicioCriado) => {
    setExercicioSelecionado({
      ...novoExercicioCriado,
      nome_exercicio: novoExercicioCriado.nome
    });
    setResultadosExercicio([]);
    setNovoExercicio("");
  };

  const handleSelecionarExercicio = (ex) => {
    setExercicioSelecionado({ ...ex, nome_exercicio: ex.nome });
    setResultadosExercicio([]);
    setNovoExercicio("");
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Criar Novo Treino</h1>

        {!alunoSelecionado ? (
          <div>
            <input
              id="buscarAluno"
              type="text"
              placeholder="Buscar aluno por nome..."
              value={buscaAluno}
              onChange={(e) => setBuscaAluno(e.target.value)}
              className="w-full border px-3 py-2 rounded"
            />
            <ul className="border mt-1 rounded max-h-40 overflow-y-auto">
              {resultadosAluno.map((aluno) => (
                <li
                  key={aluno.id_usuario}
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => setAlunoSelecionado(aluno)}
                >
                  {aluno.nome} ({aluno.cpf})
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="mb-4">
            <strong>Aluno selecionado:</strong> {alunoSelecionado.nome} ({alunoSelecionado.cpf})
          </p>
        )}

        {alunoSelecionado && (
          <>
            <div className="mb-4">
              <label htmlFor="nomeTreino" className="block mb-1 font-medium">Nome do Treino</label>
              <input
                id="nomeTreino"
                type="text"
                value={nomeTreino}
                onChange={(e) => setNomeTreino(e.target.value)}
                className="w-full border px-3 py-2 rounded"
              />
            </div>

            <div>
              <label htmlFor="novoExercicio" className="block mb-1 font-medium">Adicionar Exercício</label>
              <input
                id="novoExercicio"
                type="text"
                placeholder="Buscar exercício..."
                value={novoExercicio}
                onChange={(e) => {
                  setNovoExercicio(e.target.value);
                  setExercicioSelecionado(null);
                }}
                className="w-full border px-3 py-2 rounded"
              />

              {resultadosExercicio.length > 0 && (
                <ul className="border mt-1 rounded max-h-40 overflow-y-auto">
                  {resultadosExercicio.map((ex) => (
                    <li
                      key={ex.id_exercicio}
                      className="p-2 hover:bg-gray-100 cursor-pointer"
                      onClick={() => handleSelecionarExercicio(ex)}
                    >
                      {ex.nome}
                    </li>
                  ))}
                </ul>
              )}

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
                      <label htmlFor="series" className="block text-sm">Séries</label>
                      <input
                        id="series"
                        type="text"
                        placeholder="Séries"
                        value={formExercicio.series}
                        onChange={(e) => setFormExercicio({ ...formExercicio, series: e.target.value })}
                        className="border px-2 py-1 rounded w-full"
                      />
                    </div>
                    <div>
                      <label htmlFor="repeticoes" className="block text-sm">Repetições</label>
                      <input
                        id="repeticoes"
                        type="text"
                        placeholder="Repetições"
                        value={formExercicio.repeticoes}
                        onChange={(e) => setFormExercicio({ ...formExercicio, repeticoes: e.target.value })}
                        className="border px-2 py-1 rounded w-full"
                      />
                    </div>
                    <div>
                      <label htmlFor="observacoes" className="block text-sm">Observações</label>
                      <input
                        id="observacoes"
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
                      {e.nome_exercicio} - {e.series}x{e.repeticoes} ({e.observacoes})
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
              onClick={handleCriarTreino}
              className="mt-6 bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded"
            >
              Salvar Treino
            </button>
          </>
        )}

        <ModalCriarExercicio
          visivel={modalVisivel}
          onFechar={() => setModalVisivel(false)}
          onSalvar={handleSalvarExercicioModal}
        />
      </div>
    </Layout>
  );
}
