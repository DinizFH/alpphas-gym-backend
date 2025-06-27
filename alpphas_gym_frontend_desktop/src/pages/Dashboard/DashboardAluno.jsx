import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import {
  FaDumbbell,
  FaAppleAlt,
  FaChartLine,
  FaCalendarAlt,
  FaClipboardList,
} from "react-icons/fa";

export default function DashboardAluno() {
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [agendamentos, setAgendamentos] = useState([]);

  useEffect(() => {
    async function fetchDados() {
      try {
        const perfilRes = await api.get("/usuarios/perfil");
        setNome(perfilRes.data.nome || "");

        const agendamentosRes = await api.get("/agendamentos/");
        setAgendamentos(agendamentosRes.data || []);
      } catch (err) {
        console.error("Erro ao carregar dados do dashboard:", err);
      }
    }

    fetchDados();
  }, []);

  const proximoAgendamento = agendamentos
    .filter((a) => a.status === "marcado" || a.status === "remarcado")
    .sort((a, b) => new Date(a.data_hora_inicio) - new Date(b.data_hora_inicio))[0];

  const cards = [
    {
      title: "Treinos",
      icon: <FaDumbbell className="text-4xl text-blue-600" />,
      action: () => navigate("/treinos-aluno"),
    },
    {
      title: "Nutrição",
      icon: <FaAppleAlt className="text-4xl text-green-600" />,
      action: () => navigate("/planos"), // ✅ Caminho corrigido
    },
    {
      title: "Progresso",
      icon: <FaChartLine className="text-4xl text-purple-600" />,
      action: () => navigate("/progresso/aluno"),
    },
    {
      title: "Agendamentos",
      icon: <FaCalendarAlt className="text-4xl text-orange-500" />,
      action: () => navigate("/agendamentos-aluno"),
      info: proximoAgendamento
        ? `${new Date(proximoAgendamento.data_hora_inicio).toLocaleString()} - ${proximoAgendamento.tipo_agendamento}`
        : "Nenhum agendamento ativo",
      badge: agendamentos.filter((a) => a.status === "marcado" || a.status === "remarcado").length,
    },
    {
      title: "Registro de Treino",
      icon: <FaClipboardList className="text-4xl text-cyan-600" />,
      action: () => navigate("/registrostreino"),
    },
  ];

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Bem-vindo, {nome}!</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {cards.map((card, index) => (
            <div
              key={index}
              onClick={card.action}
              className="cursor-pointer bg-white rounded-2xl shadow-md p-6 flex flex-col items-center hover:shadow-xl transition"
            >
              {card.icon}
              <h2 className="mt-4 text-xl font-semibold">{card.title}</h2>
              {card.badge !== undefined && (
                <span className="mt-1 text-sm text-gray-500">
                  {card.badge} ativo(s)
                </span>
              )}
              {card.info && (
                <span className="mt-2 text-sm text-gray-600 text-center">
                  {card.info}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
