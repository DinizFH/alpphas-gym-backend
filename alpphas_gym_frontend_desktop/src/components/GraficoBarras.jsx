import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function GraficoBarras({ avaliacoes, campo }) {
  // Constrói os dados para o gráfico
  const data = avaliacoes.map((a, index) => ({
    nome: new Date(a.data_avaliacao).toLocaleDateString("pt-BR"),
    valor: parseFloat(a[campo]) || 0,     // garante que sempre terá número
  }));

  // Verifica se todos os valores são 0 ou inválidos
  const temDadosValidos = data.some((d) => d.valor > 0);

  if (!temDadosValidos) {
    return (
      <div className="bg-white p-4 shadow rounded">
        <h4 className="text-md font-semibold mb-2">
          {campo.replace(/_/g, " ").toUpperCase()}
        </h4>
        <p className="text-sm text-gray-500">Sem dados disponíveis.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 shadow rounded">
      <h4 className="text-md font-semibold mb-2">
        {campo.replace(/_/g, " ").toUpperCase()}
      </h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <XAxis dataKey="nome" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="valor" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
