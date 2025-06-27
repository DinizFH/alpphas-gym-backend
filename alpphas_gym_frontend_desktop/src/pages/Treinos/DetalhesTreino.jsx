import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function DetalhesTreino() {
  const { id } = useParams();
  const [treino, setTreino] = useState(null);
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    async function fetchDados() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setUsuario(perfil.data);
        const res = await api.get(`/treinos/${id}`);
        setTreino(res.data);
      } catch (err) {
        console.error("Erro ao carregar detalhes do treino:", err);
      }
    }
    fetchDados();
  }, [id]);

  if (!treino || !usuario) return <div>Carregando...</div>;

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Detalhes do Treino</h1>

        <div className="mb-4">
          <p><strong>Nome do Treino:</strong> {treino.nome_treino}</p>
          {treino.nome_aluno && (
            <p><strong>Aluno:</strong> {treino.nome_aluno} ({treino.cpf_aluno})</p>
          )}
        </div>

        <h3 className="font-semibold text-lg mb-2">Exercícios</h3>
        <ul className="list-disc ml-6 space-y-1">
          {treino.exercicios.map((ex, index) => (
            <li key={index}>
              <span className="font-medium">{ex.nome_exercicio || ex.nome}</span> - {ex.series}x{ex.repeticoes} ({ex.observacoes})
            </li>
          ))}
        </ul>
      </div>
    </Layout>
  );
}
