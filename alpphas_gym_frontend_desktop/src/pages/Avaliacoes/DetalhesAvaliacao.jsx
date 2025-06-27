import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer
} from "recharts";

export default function DetalhesAvaliacao() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [avaliacao, setAvaliacao] = useState(null);
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const resAvaliacao = await api.get(`/avaliacoes/${id}`);
        setAvaliacao(resAvaliacao.data);

        const resPerfil = await api.get("/usuarios/perfil");
        setUsuario(resPerfil.data);
      } catch (err) {
        console.error("Erro ao carregar detalhes da avaliação", err);
      }
    }
    fetchData();
  }, [id]);

  const handleExcluir = async () => {
    if (window.confirm("Tem certeza que deseja excluir esta avaliação?")) {
      try {
        await api.delete(`/avaliacoes/${id}`);
        navigate("/avaliacoes");
      } catch (err) {
        console.error("Erro ao excluir avaliação", err);
      }
    }
  };

  const handleEditar = () => {
    navigate(`/avaliacoes/${id}/editar`);
  };

  if (!avaliacao || !usuario) return <div>Carregando...</div>;

  const podeEditarOuExcluir =
    usuario.tipo_usuario === "personal" || usuario.tipo_usuario === "nutricionista";

  const gordura = parseFloat(avaliacao.percentual_gordura) || 0;
  const magra = 100 - gordura;
  const dadosPizza = [
    { nome: "Gordura Corporal", valor: gordura },
    { nome: "Massa Magra", valor: magra }
  ];
  const cores = ["#E53E3E", "#38A169"];

  return (
    <Layout>
      <div className="max-w-4xl mx-auto bg-white p-8 shadow-md rounded mt-6">
        <h2 className="text-2xl font-bold mb-6">Detalhes da Avaliação</h2>

        <p><strong>Aluno Avaliado:</strong> {avaliacao.nome_aluno}</p>
        <p><strong>CPF do Aluno:</strong> {avaliacao.cpf_aluno}</p>
        <p><strong>Profissional Responsável:</strong> {avaliacao.nome_profissional}</p>
        <hr className="my-4" />

        <div className="grid grid-cols-2 gap-4">
          <p><strong>Peso:</strong> {avaliacao.peso} kg</p>
          <p><strong>Altura:</strong> {avaliacao.altura} m</p>
          <p><strong>Idade:</strong> {avaliacao.idade} anos</p>

          <p><strong>IMC:</strong> {avaliacao.imc}</p>
          <p><strong>% Gordura:</strong> {avaliacao.percentual_gordura} %</p>
          <p><strong>Massa Magra:</strong> {avaliacao.massa_magra} kg</p>
          <p><strong>Massa Gorda:</strong> {avaliacao.massa_gorda} kg</p>

          <p><strong>Dobra Peitoral:</strong> {avaliacao.dobra_peitoral} mm</p>
          <p><strong>Dobra Tríceps:</strong> {avaliacao.dobra_triceps} mm</p>
          <p><strong>Dobra Subescapular:</strong> {avaliacao.dobra_subescapular} mm</p>
          <p><strong>Dobra Bíceps:</strong> {avaliacao.dobra_biceps} mm</p>
          <p><strong>Dobra Axilar Média:</strong> {avaliacao.dobra_axilar_media} mm</p>
          <p><strong>Dobra Supra-ilíaca:</strong> {avaliacao.dobra_supra_iliaca} mm</p>

          <p><strong>Pescoço:</strong> {avaliacao.pescoco} cm</p>
          <p><strong>Ombro:</strong> {avaliacao.ombro} cm</p>
          <p><strong>Tórax:</strong> {avaliacao.torax} cm</p>
          <p><strong>Cintura:</strong> {avaliacao.cintura} cm</p>
          <p><strong>Abdômen:</strong> {avaliacao.abdomen} cm</p>
          <p><strong>Quadril:</strong> {avaliacao.quadril} cm</p>
          <p><strong>Braço D:</strong> {avaliacao.braco_direto} cm</p>
          <p><strong>Braço E:</strong> {avaliacao.braco_esquerdo} cm</p>
          <p><strong>Braço Direito Contraído:</strong> {avaliacao.braco_d_contraido} cm</p>
          <p><strong>Braço Esquerdo Contraído:</strong> {avaliacao.braco_e_contraido} cm</p>
          <p><strong>Antebraço D:</strong> {avaliacao.antebraco_direito} cm</p>
          <p><strong>Antebraço E:</strong> {avaliacao.antebraco_esquerdo} cm</p>
          <p><strong>Coxa D:</strong> {avaliacao.coxa_direita} cm</p>
          <p><strong>Coxa E:</strong> {avaliacao.coxa_esquerda} cm</p>
          <p><strong>Panturrilha D:</strong> {avaliacao.panturrilha_direita} cm</p>
          <p><strong>Panturrilha E:</strong> {avaliacao.panturrilha_esquerda} cm</p>
        </div>

        <div className="mt-6">
          <p><strong>Observações:</strong></p>
          <p className="bg-gray-100 p-4 rounded">{avaliacao.observacoes || "Nenhuma observação registrada."}</p>
        </div>

        {/* Gráfico de Composição Corporal */}
        <div className="mt-10">
          <h3 className="text-xl font-bold mb-4">Composição Corporal</h3>
          <div className="w-full h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={dadosPizza}
                  dataKey="valor"
                  nameKey="nome"
                  outerRadius={90}
                  label
                >
                  {dadosPizza.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={cores[index % cores.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {podeEditarOuExcluir && (
          <div className="mt-6 flex gap-4">
            <button
              onClick={handleEditar}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              Editar
            </button>
            <button
              onClick={handleExcluir}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
            >
              Excluir
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
