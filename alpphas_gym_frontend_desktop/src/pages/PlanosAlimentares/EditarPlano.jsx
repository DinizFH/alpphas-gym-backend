import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function EditarPlano() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plano, setPlano] = useState(null);

  useEffect(() => {
    async function carregarPlano() {
      try {
        const res = await api.get(`/planos/${id}`);
        setPlano(res.data);
      } catch (err) {
        console.error("Erro ao carregar plano:", err);
        alert("Erro ao carregar plano alimentar.");
      }
    }
    carregarPlano();
  }, [id]);

  const handleRefeicaoChange = (index, campo, valor) => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes[index][campo] = valor;
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const handleAlimentoChange = (refIndex, alimIndex, campo, valor) => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes[refIndex].alimentos[alimIndex][campo] = valor;
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const adicionarAlimento = (refIndex) => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes[refIndex].alimentos.push({ nome: "", peso: "" });
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const removerAlimento = (refIndex, alimIndex) => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes[refIndex].alimentos.splice(alimIndex, 1);
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const adicionarRefeicao = () => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes.push({
      titulo: "",
      calorias_estimadas: "",
      alimentos: [{ nome: "", peso: "" }],
    });
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const removerRefeicao = (index) => {
    const novasRefeicoes = [...plano.refeicoes];
    novasRefeicoes.splice(index, 1);
    setPlano({ ...plano, refeicoes: novasRefeicoes });
  };

  const salvarAlteracoes = async () => {
    // ⚠️ Filtra refeições sem alimentos válidos
    const refeicoesValidas = plano.refeicoes
      .filter(ref => ref.titulo.trim() && ref.alimentos.length > 0)
      .map(ref => ({
        ...ref,
        alimentos: ref.alimentos.filter(alim => alim.nome.trim() && alim.peso)
      }))
      .filter(ref => ref.alimentos.length > 0);

    if (refeicoesValidas.length === 0) {
      alert("Informe ao menos uma refeição com alimentos válidos.");
      return;
    }

    try {
      await api.put(`/planos/${id}`, { refeicoes: refeicoesValidas });
      alert("Plano atualizado com sucesso!");
      navigate("/planos");
    } catch (err) {
      console.error("Erro ao atualizar plano:", err);
      alert("Erro ao atualizar plano.");
    }
  };

  if (!plano) {
    return (
      <Layout>
        <div className="p-6">Carregando plano alimentar...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 max-w-4xl mx-auto bg-white shadow rounded">
        <h1 className="text-2xl font-bold mb-4">Editar Plano Alimentar</h1>

        <div className="space-y-6">
          {plano.refeicoes.map((ref, refIndex) => (
            <div key={refIndex} className="border p-4 rounded bg-gray-50">
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-lg font-semibold">Refeição {refIndex + 1}</h2>
                <button
                  onClick={() => removerRefeicao(refIndex)}
                  className="text-red-600 underline"
                >
                  Remover
                </button>
              </div>

              <input
                type="text"
                value={ref.titulo}
                onChange={(e) =>
                  handleRefeicaoChange(refIndex, "titulo", e.target.value)
                }
                placeholder="Ex: Café da manhã"
                className="w-full p-2 border rounded mb-2"
              />

              <input
                type="number"
                value={ref.calorias_estimadas}
                onChange={(e) =>
                  handleRefeicaoChange(refIndex, "calorias_estimadas", e.target.value)
                }
                placeholder="Calorias estimadas"
                className="w-full p-2 border rounded mb-4"
              />

              <div className="space-y-2">
                {ref.alimentos.map((alimento, alimIndex) => (
                  <div key={alimIndex} className="flex gap-2 items-center">
                    <input
                      type="text"
                      value={alimento.nome}
                      onChange={(e) =>
                        handleAlimentoChange(refIndex, alimIndex, "nome", e.target.value)
                      }
                      placeholder={`Alimento ${alimIndex + 1}`}
                      className="flex-1 p-2 border rounded"
                    />
                    <input
                      type="text"
                      value={alimento.peso}
                      onChange={(e) =>
                        handleAlimentoChange(refIndex, alimIndex, "peso", e.target.value)
                      }
                      placeholder="Peso (g/ml)"
                      className="w-32 p-2 border rounded"
                    />
                    <button
                      className="text-red-600 text-sm underline"
                      onClick={() => removerAlimento(refIndex, alimIndex)}
                    >
                      Remover
                    </button>
                  </div>
                ))}
              </div>

              <button
                onClick={() => adicionarAlimento(refIndex)}
                className="text-sm text-blue-600 mt-2"
              >
                + Adicionar Alimento
              </button>
            </div>
          ))}

          <button
            onClick={adicionarRefeicao}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Nova Refeição
          </button>

          <div className="mt-6 flex justify-between">
            <button
              onClick={() => navigate("/planos")}
              className="text-gray-600 hover:text-black"
            >
              Cancelar
            </button>
            <button
              onClick={salvarAlteracoes}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Salvar Alterações
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
