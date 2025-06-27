import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";

export default function DetalhesRegistroTreino() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [registro, setRegistro] = useState(null);
  const [tipoUsuario, setTipoUsuario] = useState("");

  useEffect(() => {
    async function carregarRegistro() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setTipoUsuario(perfil.data.tipo_usuario);

        const res = await api.get(`/registrostreino/${id}`);
        setRegistro(res.data);
      } catch (err) {
        console.error("Erro ao carregar registro:", err);
        alert("Erro ao carregar registro.");
        navigate("/registrostreino");
      }
    }

    carregarRegistro();
  }, [id, navigate]);

  const handleEditar = () => {
    navigate(`/registrostreino/${id}/editar`);
  };

  const handleExcluir = async () => {
    const confirmar = window.confirm("Tem certeza que deseja excluir este registro?");
    if (!confirmar) return;

    try {
      await api.delete(`/registrostreino/${id}`);
      alert("Registro excluído com sucesso.");
      navigate("/registrostreino");
    } catch (err) {
      console.error("Erro ao excluir registro:", err);
      alert("Erro ao excluir registro.");
    }
  };

  if (!registro) return <p className="p-6">Carregando registro...</p>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Detalhes do Registro de Treino</h1>
        {(tipoUsuario === "aluno" || tipoUsuario === "personal") && (
          <div className="flex gap-2">
            <button
              onClick={handleEditar}
              className="bg-yellow-500 text-white px-4 py-1 rounded hover:bg-yellow-600"
            >
              Editar
            </button>
            <button
              onClick={handleExcluir}
              className="bg-red-500 text-white px-4 py-1 rounded hover:bg-red-600"
            >
              Excluir
            </button>
          </div>
        )}
      </div>

      <div className="bg-white p-4 rounded shadow mb-6">
        <p><strong>Aluno:</strong> {registro.nome_aluno}</p>
        <p><strong>Treino:</strong> {registro.nome_treino}</p>
        <p><strong>Data:</strong> {new Date(registro.data_execucao).toLocaleString()}</p>
        {registro.nome_profissional && (
          <p><strong>Profissional:</strong> {registro.nome_profissional}</p>
        )}
        {registro.observacoes && (
          <p className="mt-2"><strong>Observações:</strong> {registro.observacoes}</p>
        )}
      </div>

      <h2 className="text-xl font-semibold mb-3">Exercícios Realizados</h2>
      <div className="grid gap-4">
        {registro.exercicios.map((ex) => (
          <div key={ex.id_exercicio} className="bg-gray-100 p-3 rounded">
            <p><strong>Exercício:</strong> {ex.nome}</p>
            <p><strong>Grupo Muscular:</strong> {ex.grupo_muscular}</p>
            <p><strong>Carga Utilizada:</strong> {ex.carga} kg</p>
          </div>
        ))}
      </div>
    </div>
  );
}
