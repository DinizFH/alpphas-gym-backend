import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function GraficoPizza({ massa_magra, massa_gorda, data }) {
  const dataPizza = [
    { nome: "Massa Magra", valor: parseFloat(massa_magra) },
    { nome: "Massa Gorda", valor: parseFloat(massa_gorda) },
  ];

  const cores = ["#38A169", "#E53E3E"];

  return (
    <div className="w-full h-64">
      <h3 className="text-xl font-semibold mb-2">
        Composição Corporal (Avaliação {new Date(data).toLocaleDateString("pt-BR")})
      </h3>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={dataPizza}
            dataKey="valor"
            nameKey="nome"
            outerRadius={100}
            label
          >
            {cores.map((cor, i) => (
              <Cell key={i} fill={cor} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
