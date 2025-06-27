import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function TreinosAluno() {
  const [treinos, setTreinos] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function buscarTreinos() {
      try {
        const res = await api.get("/treinos/aluno");
        setTreinos(res.data);
      } catch (err) {
        console.error("Erro ao carregar treinos do aluno:", err);
      }
    }

    buscarTreinos();
  }, []);

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Meus Treinos</h1>

        {treinos.length === 0 ? (
          <p>Você ainda não possui treinos cadastrados.</p>
        ) : (
          <ul className="space-y-4">
            {treinos.map((treino) => (
              <li
                key={treino.id_treino}
                className="bg-white p-4 rounded shadow flex justify-between items-center"
              >
                <span className="font-medium">{treino.nome_treino}</span>
                <button
                  onClick={() => navigate(`/treinos/${treino.id_treino}`)}
                  className="text-blue-600 hover:underline text-sm"
                >
                  Ver detalhes
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  );
}
