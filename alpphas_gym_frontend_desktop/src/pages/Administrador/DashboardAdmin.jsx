import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import {
  FaUsers,
  FaUserTie,
  FaUserMd,
  FaDumbbell,
  FaClipboardList,
  FaCalendarAlt,
  FaHeartbeat,
} from "react-icons/fa";

export default function DashboardAdmin() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    alunos: 0,
    personal: 0,
    nutricionista: 0,
    treinos: 0,
    planos: 0,
    agendamentos: 0,
    avaliacoes: 0,
    exercicios: 0,
  });

  useEffect(() => {
    const tipo = localStorage.getItem("perfil_tipo");
    if (tipo !== "admin") {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    async function fetchEstatisticas() {
      try {
        const res = await api.get("/admin/estatisticas");
        setStats(res.data);
      } catch (err) {
        console.error("Erro ao carregar estatísticas:", err);
      }
    }
    fetchEstatisticas();
  }, []);

  const cards = [
    { label: "Alunos", valor: stats.alunos, icon: <FaUsers /> },
    { label: "Personais", valor: stats.personal, icon: <FaUserTie /> },
    { label: "Nutricionistas", valor: stats.nutricionista, icon: <FaUserMd /> },
    { label: "Treinos", valor: stats.treinos, icon: <FaDumbbell /> },
    { label: "Exercícios", valor: stats.exercicios, icon: <FaDumbbell /> },
    { label: "Planos Alimentares", valor: stats.planos, icon: <FaClipboardList /> },
    { label: "Agendamentos", valor: stats.agendamentos, icon: <FaCalendarAlt /> },
    { label: "Avaliações Físicas", valor: stats.avaliacoes, icon: <FaHeartbeat /> },
  ];

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Dashboard do Administrador</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {cards.map((card, index) => (
            <div
              key={index}
              className="bg-white shadow-md p-5 rounded-2xl flex items-center justify-between hover:shadow-lg transition"
              aria-label={`${card.label}: ${card.valor}`}
            >
              <div className="text-4xl text-blue-600">{card.icon}</div>
              <div className="text-right">
                <div className="text-sm text-gray-500">{card.label}</div>
                <div className="text-2xl font-bold">{card.valor}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
