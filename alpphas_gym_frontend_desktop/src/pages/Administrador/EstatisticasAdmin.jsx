import { useEffect, useState } from "react";
import api from "../../axios";
import Layout from "../../components/Layout";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function EstatisticasAdmin() {
  const [dados, setDados] = useState(null);

  useEffect(() => {
    async function fetchEstatisticas() {
      try {
        const res = await api.get("/admin/estatisticas");
        setDados(res.data);
      } catch (err) {
        console.error("Erro ao carregar estatísticas:", err);
      }
    }
    fetchEstatisticas();
  }, []);

  if (!dados) return <Layout><p className="p-4">Carregando...</p></Layout>;

  const cores = ["#4F46E5", "#10B981", "#F59E0B"];
  const dataPizza = [
    { name: "Alunos", value: dados.alunos, fill: cores[0] },
    { name: "Personais", value: dados.personal, fill: cores[1] },
    { name: "Nutricionistas", value: dados.nutricionista, fill: cores[2] },
  ];

  const dataBarra = [
    { nome: "Treinos", total: dados.treinos },
    { nome: "Avaliações", total: dados.avaliacoes },
    { nome: "Registros", total: dados.registros || 0 },
    { nome: "Planos", total: dados.planos },
  ];

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-semibold mb-6">Estatísticas Gerais</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card titulo="Alunos" valor={dados.alunos} />
          <Card titulo="Personais" valor={dados.personal} />
          <Card titulo="Nutricionistas" valor={dados.nutricionista} />
          <Card titulo="Treinos" valor={dados.treinos} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-4 text-center">Usuários por Tipo</h2>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={dataPizza} dataKey="value" outerRadius={90} label>
                  {dataPizza.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-4 text-center">Atividades do Sistema</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={dataBarra}>
                <XAxis dataKey="nome" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" fill="#4F46E5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function Card({ titulo, valor }) {
  return (
    <div className="bg-white p-4 rounded shadow text-center">
      <h3 className="text-sm text-gray-600">{titulo}</h3>
      <p className="text-2xl font-bold text-blue-600">{valor}</p>
    </div>
  );
}
