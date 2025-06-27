import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import {
  FaCalendarAlt,
  FaAppleAlt,
  FaUserCheck,
  FaChartLine,
} from "react-icons/fa";

export default function DashboardNutricionista() {
  const navigate = useNavigate();
  const [nome, setNome] = useState("");

  useEffect(() => {
    async function fetchPerfil() {
      try {
        const res = await api.get("/usuarios/perfil");
        setNome(res.data.nome);
      } catch (err) {
        console.error("Erro ao buscar perfil:", err);
      }
    }
    fetchPerfil();
  }, []);

  const cards = [
    {
      title: "Agendamentos",
      icon: <FaCalendarAlt className="text-4xl text-blue-600" />,
      action: () => navigate("/agendamentos"),
    },
    {
      title: "Planos Alimentares",
      icon: <FaAppleAlt className="text-4xl text-green-600" />,
      action: () => navigate("/planos"),
    },
    {
      title: "Avaliações",
      icon: <FaUserCheck className="text-4xl text-purple-600" />,
      action: () => navigate("/avaliacoes"),
    },
    {
      title: "Progresso",
      icon: <FaChartLine className="text-4xl text-emerald-600" />,
      action: () => navigate("/progresso"),
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
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
