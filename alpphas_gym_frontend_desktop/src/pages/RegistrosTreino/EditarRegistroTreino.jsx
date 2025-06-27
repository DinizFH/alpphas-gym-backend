import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";

export default function EditarRegistroTreino() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [exercicios, setExercicios] = useState([]);
  const [cargas, setCargas] = useState({});
  const [nomeTreino, setNomeTreino] = useState("");
  const [observacoes, setObservacoes] = useState("");

  useEffect(() => {
    async function carregarRegistro() {
      try {
        const res = await api.get(`/registrostreino/${id}`);
        setNomeTreino(res.data.nome_treino);
        setObservacoes(res.data.observacoes || "");

        const cargasExistentes = {};
        const listaExercicios = res.data.exercicios || [];

        listaExercicios.forEach((ex) => {
          cargasExistentes[ex.id_exercicio] = ex.carga;
        });

        setCargas(cargasExistentes);
        setExercicios(listaExercicios);
      } catch (err) {
        console.error("Erro ao carregar registro:", err);
        alert("Erro ao carregar registro.");
        navigate("/registrostreino");
      }
    }

    carregarRegistro();
  }, [id, navigate]);

  const handleChangeCarga = (id_exercicio, valor) => {
    setCargas((prev) => ({
      ...prev,
      [id_exercicio]: valor,
    }));
  };

  const handleSalvar = async () => {
    try {
      const payload = {
        observacoes,
        cargas: exercicios.map((ex) => ({
          id_exercicio: ex.id_exercicio,
          carga: parseFloat(cargas[ex.id_exercicio]) || 0,
        })),
      };

      await api.put(`/registrostreino/${id}`, payload);
      alert("Registro de treino atualizado com sucesso!");
      navigate("/registrostreino");
    } catch (err) {
      console.error("Erro ao atualizar registro:", err);
      alert("Erro ao atualizar registro.");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Editar Registro: {nomeTreino}</h1>

      <div className="mb-6">
        <label className="block mb-1 font-medium">Observações</label>
        <textarea
          className="w-full border border-gray-300 p-2 rounded"
          rows={3}
          value={observacoes}
          onChange={(e) => setObservacoes(e.target.value)}
        />
      </div>

      {exercicios.length === 0 ? (
        <p className="text-gray-600">Nenhum exercício neste registro.</p>
      ) : (
        <div className="space-y-4">
          {exercicios.map((ex) => (
            <div
              key={ex.id_exercicio}
              className="bg-white p-4 shadow rounded flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            >
              <div className="flex-1">
                <p className="font-semibold">{ex.nome}</p>
                <p className="text-sm text-gray-500">Grupo: {ex.grupo_muscular}</p>
              </div>
              <input
                type="number"
                step="0.1"
                placeholder="Carga (kg)"
                value={cargas[ex.id_exercicio] || ""}
                onChange={(e) => handleChangeCarga(ex.id_exercicio, e.target.value)}
                className="border border-gray-300 p-2 rounded w-full md:w-40"
              />
            </div>
          ))}
        </div>
      )}

      <div className="text-right mt-6">
        <button
          onClick={handleSalvar}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Salvar Alterações
        </button>
      </div>
    </div>
  );
}
