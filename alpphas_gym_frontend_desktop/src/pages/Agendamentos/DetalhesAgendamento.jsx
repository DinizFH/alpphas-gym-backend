import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function DetalhesAgendamento() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [agendamento, setAgendamento] = useState(null);
  const [tipoUsuario, setTipoUsuario] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setTipoUsuario(perfil.data.tipo_usuario);

        const res = await api.get(`/agendamentos/${id}`);
        setAgendamento(res.data);
      } catch (err) {
        console.error("Erro ao carregar agendamento:", err);
        alert("Erro ao carregar detalhes do agendamento.");
      }
    }

    fetchData();
  }, [id]);

  const cancelar = async () => {
    if (!window.confirm("Deseja realmente cancelar este agendamento?")) return;
    try {
      await api.delete(`/agendamentos/${id}`);
      alert("Agendamento cancelado com sucesso!");
      navigate("/agendamentos");
    } catch (err) {
      console.error("Erro ao cancelar:", err);
      alert("Erro ao cancelar agendamento.");
    }
  };

  if (!agendamento) {
    return (
      <Layout>
        <div className="p-6">Carregando agendamento...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 max-w-2xl mx-auto bg-white rounded shadow">
        <h1 className="text-2xl font-bold mb-4">Detalhes do Agendamento</h1>

        <div className="space-y-2 text-gray-700">
          <p>
            <strong>Aluno:</strong> {agendamento.nome_aluno || "Não identificado"}
          </p>
          <p>
            <strong>Profissional:</strong> {agendamento.nome_profissional || "Não identificado"}
          </p>
          <p>
            <strong>Tipo:</strong> {agendamento.tipo_agendamento}
          </p>
          <p>
            <strong>Início:</strong>{" "}
            {new Date(agendamento.data_hora_inicio).toLocaleString()}
          </p>
          <p>
            <strong>Término:</strong>{" "}
            {new Date(agendamento.data_hora_fim).toLocaleString()}
          </p>
          <p>
            <strong>Status:</strong>{" "}
            <span
              className={`font-semibold ${
                agendamento.status === "cancelado"
                  ? "text-red-600"
                  : agendamento.status === "concluído"
                  ? "text-blue-600"
                  : "text-green-600"
              }`}
            >
              {(agendamento.status || "indefinido").toUpperCase()}
            </span>
          </p>
        </div>

        {(agendamento.status === "marcado" || agendamento.status === "remarcado") && (
          <div className="mt-6 flex gap-4">
            {(tipoUsuario === "personal" || tipoUsuario === "nutricionista") && (
              <button
                onClick={() => navigate(`/agendamentos/${id}/editar`)}
                className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
              >
                Editar
              </button>
            )}

            <button
              onClick={cancelar}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Cancelar
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
