import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function AgendamentosAluno() {
  const [agendamentos, setAgendamentos] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchAgendamentos() {
      try {
        const res = await api.get("/agendamentos/");
        setAgendamentos(res.data);
      } catch (error) {
        console.error("Erro ao buscar agendamentos do aluno:", error);
        alert("Erro ao buscar agendamentos.");
      }
    }

    fetchAgendamentos();
  }, []);

  const cancelarAgendamento = async (id_agendamento) => {
    if (!window.confirm("Tem certeza que deseja cancelar este agendamento?")) return;
    try {
      await api.delete(`/agendamentos/${id_agendamento}`);
      setAgendamentos((prev) =>
        prev.map((a) =>
          a.id_agendamento === id_agendamento ? { ...a, status: "cancelado" } : a
        )
      );
    } catch (err) {
      console.error("Erro ao cancelar agendamento:", err);
      alert("Erro ao cancelar agendamento.");
    }
  };

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Meus Agendamentos</h1>

        {agendamentos.length === 0 ? (
          <p className="text-gray-600">Nenhum agendamento encontrado.</p>
        ) : (
          <div className="grid gap-4">
            {agendamentos.map((agendamento) => {
              const status = agendamento.status || "indefinido";
              let statusClass = "text-gray-600";
              if (status === "cancelado") statusClass = "text-red-600";
              else if (status === "concluído") statusClass = "text-blue-600";
              else if (status === "remarcado" || status === "marcado") statusClass = "text-green-600";

              const tipo = agendamento.tipo_agendamento || "Indefinido";
              const nomeProfissional = agendamento.nome_profissional || "Não identificado";

              return (
                <div
                  key={agendamento.id_agendamento}
                  className="bg-white p-4 rounded shadow flex flex-col sm:flex-row justify-between items-start sm:items-center"
                >
                  <div>
                    <p className="font-semibold">Profissional: {nomeProfissional}</p>
                    <p className="text-sm text-gray-600">Tipo: {tipo}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(agendamento.data_hora_inicio).toLocaleString()} até{" "}
                      {new Date(agendamento.data_hora_fim).toLocaleTimeString()}
                    </p>
                    <p className={`text-sm mt-1 ${statusClass}`}>
                      {status.toUpperCase()}
                    </p>
                  </div>

                  <div className="flex gap-2 mt-4 sm:mt-0">
                    <button
                      onClick={() => navigate(`/agendamentos/${agendamento.id_agendamento}`)}
                      className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 text-sm font-medium"
                    >
                      Detalhes
                    </button>

                    {(status === "marcado" || status === "remarcado") && (
                      <button
                        onClick={() => cancelarAgendamento(agendamento.id_agendamento)}
                        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm font-medium"
                      >
                        Cancelar
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
}
