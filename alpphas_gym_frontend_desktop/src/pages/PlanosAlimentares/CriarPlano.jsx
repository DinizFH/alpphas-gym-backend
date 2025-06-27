import { useState } from "react";
import api from "../../axios";

export default function CriarPlano({ aluno, onCancel, onClose, onPlanoCriado }) {
  const [descricaoGeral, setDescricaoGeral] = useState("");
  const [refeicoes, setRefeicoes] = useState([]);
  const [novaRefeicao, setNovaRefeicao] = useState({
    titulo: "",
    calorias_estimadas: "",
    alimentos: Array.from({ length: 5 }, () => ({ nome: "", peso: "" })),
  });

  const handleAlimentoChange = (index, campo, valor) => {
    const novosAlimentos = [...novaRefeicao.alimentos];
    novosAlimentos[index][campo] = valor;
    setNovaRefeicao({ ...novaRefeicao, alimentos: novosAlimentos });
  };

  const adicionarAlimento = () => {
    setNovaRefeicao((prev) => ({
      ...prev,
      alimentos: [...prev.alimentos, { nome: "", peso: "" }],
    }));
  };

  const adicionarRefeicao = () => {
  if (!novaRefeicao.titulo.trim()) return;

  const alimentosValidos = novaRefeicao.alimentos.filter(
    (a) => a.nome.trim() !== "" && a.peso.trim() !== ""
  );
  if (alimentosValidos.length === 0) return;

  setRefeicoes((prev) => [
    ...prev,
    {
      ...novaRefeicao,
      calorias_estimadas: Number(novaRefeicao.calorias_estimadas),
      alimentos: alimentosValidos
    },
  ]);

  setNovaRefeicao({
    titulo: "",
    calorias_estimadas: "",
    alimentos: Array.from({ length: 5 }, () => ({ nome: "", peso: "" })),
  });
};

  const salvarPlano = async () => {
  try {
    const refeicoesFiltradas = refeicoes
      .map((r) => ({
        ...r,
        calorias_estimadas: Number(r.calorias_estimadas),
        alimentos: r.alimentos.filter(
          (a) => a.nome.trim() !== "" && a.peso.trim() !== ""
        ),
      }))
      .filter((r) => r.alimentos.length > 0); // não envia refeições sem alimentos

    if (refeicoesFiltradas.length === 0) {
      alert("Adicione ao menos uma refeição com alimentos válidos.");
      return;
    }

    const body = {
      id_aluno: aluno.id_usuario,
      descricao_geral: descricaoGeral,
      refeicoes: refeicoesFiltradas,
    };

    await api.post("/planos/", body);
    alert("Plano alimentar criado com sucesso!");

    if (onPlanoCriado) onPlanoCriado();
    onClose();
  } catch (err) {
    console.error("Erro ao salvar plano:", err);
    alert("Erro ao salvar plano.");
  }
};

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Criar Plano Alimentar</h2>
      <p className="mb-4 text-sm text-gray-600">
        Criando para: <strong>{aluno.nome}</strong> | CPF: {aluno.cpf}
      </p>

      <textarea
        placeholder="Descrição geral do plano (opcional)"
        value={descricaoGeral}
        onChange={(e) => setDescricaoGeral(e.target.value)}
        className="w-full p-2 border rounded mb-4"
        rows={3}
      />

      <div className="space-y-4">
        <input
          type="text"
          placeholder="Título da refeição (Ex: Café da manhã)"
          value={novaRefeicao.titulo}
          onChange={(e) =>
            setNovaRefeicao({ ...novaRefeicao, titulo: e.target.value })
          }
          className="w-full p-2 border rounded"
        />

        <input
          type="number"
          placeholder="Calorias totais da refeição"
          value={novaRefeicao.calorias_estimadas}
          onChange={(e) =>
            setNovaRefeicao({
              ...novaRefeicao,
              calorias_estimadas: e.target.value,
            })
          }
          className="w-full p-2 border rounded"
        />

        <div className="space-y-2">
          {novaRefeicao.alimentos.map((alimento, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                placeholder={`Alimento ${index + 1}`}
                value={alimento.nome}
                onChange={(e) =>
                  handleAlimentoChange(index, "nome", e.target.value)
                }
                className="flex-1 p-2 border rounded"
              />
              <input
                type="text"
                placeholder="Peso (g/ml)"
                value={alimento.peso}
                onChange={(e) =>
                  handleAlimentoChange(index, "peso", e.target.value)
                }
                className="w-32 p-2 border rounded"
              />
            </div>
          ))}

          {novaRefeicao.alimentos.length >= 5 && (
            <button
              onClick={adicionarAlimento}
              className="text-sm text-blue-600"
            >
              + Adicionar mais alimentos
            </button>
          )}
        </div>

        <button
          onClick={adicionarRefeicao}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Adicionar Refeição
        </button>

        {refeicoes.length > 0 && (
          <div className="bg-gray-50 p-4 border rounded">
            <h3 className="font-semibold mb-2">Refeições adicionadas:</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {refeicoes.map((r, i) => (
                <li key={i}>
                  <strong>{r.titulo}</strong> — {r.calorias_estimadas} kcal,{" "}
                  {r.alimentos.length} alimentos
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-between mt-6">
          <button
            onClick={onCancel}
            className="text-gray-600 hover:text-black"
          >
            Voltar
          </button>
          <button
            onClick={salvarPlano}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Salvar Plano Completo
          </button>
        </div>
      </div>
    </div>
  );
}
