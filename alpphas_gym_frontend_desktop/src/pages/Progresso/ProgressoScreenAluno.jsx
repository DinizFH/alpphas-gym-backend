import { useState, useEffect } from "react";
import api from "../../axios";
import Layout from "../../components/Layout";
import GraficoPizza from "../../components/GraficoPizza";
import GraficoBarras from "../../components/GraficoBarras";

export default function ProgressoScreenAluno() {
  const [avaliacoes, setAvaliacoes] = useState([]);
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    async function fetchDados() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setUsuario(perfil.data);
        const res = await api.get(`/avaliacoes/evolucao/${perfil.data.id_usuario}`);
        const ultimas = res.data.avaliacoes.slice(-4);
        setAvaliacoes(ultimas);
      } catch (err) {
        console.error("Erro ao buscar progresso", err);
      }
    }
    fetchDados();
  }, []);

  const ultima = avaliacoes.length ? avaliacoes[avaliacoes.length - 1] : null;
  const penultima = avaliacoes.length > 1 ? avaliacoes[avaliacoes.length - 2] : null;

  const comparar = (campo) => {
    if (!ultima || !penultima) return null;
    const valorAtual = parseFloat(ultima[campo]);
    const valorAnterior = parseFloat(penultima[campo]);
    const diff = valorAtual - valorAnterior;
    const simbolo = diff > 0 ? "📈" : diff < 0 ? "📉" : "➖";
    return `${valorAtual.toFixed(2)} ${simbolo} ${diff.toFixed(2)}`;
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Meu Progresso</h1>

        {ultima && (
          <div className="mb-8">
            <GraficoPizza
              massa_magra={ultima.massa_magra}
              massa_gorda={ultima.massa_gorda}
              data={ultima.data_avaliacao}
            />
          </div>
        )}

        {ultima && penultima && (
          <div className="mb-10 bg-white shadow rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">Resumo da Última Avaliação</h3>
            <ul className="text-sm space-y-1">
              <li><strong>IMC:</strong> {comparar("imc")}</li>
              <li><strong>Massa Magra:</strong> {comparar("massa_magra")} kg</li>
              <li><strong>% Gordura:</strong> {comparar("percentual_gordura")} %</li>
              <li><strong>Braço D (contraído):</strong> {comparar("braco_d_contraido")} cm</li>
              <li><strong>Braço E (contraído):</strong> {comparar("braco_e_contraido")} cm</li>
            </ul>
          </div>
        )}

        {avaliacoes.length > 1 && (
          <div className="space-y-10">
            {[
              "imc",
              "percentual_gordura",
              "massa_magra",
              "massa_gorda",
              "ombro",
              "torax",
              "cintura",
              "abdomen",
              "quadril",
              "braco_direito",
              "braco_esquerdo",
              "braco_d_contraido",
              "braco_e_contraido",
              "antebraco_direito",
              "antebraco_esquerdo",
              "coxa_direita",
              "coxa_esquerda",
              "panturrilha_direita",
              "panturrilha_esquerda"
            ].map((campo) => (
              <GraficoBarras key={campo} avaliacoes={avaliacoes} campo={campo} />
            ))}
          </div>
        )}

        {avaliacoes.length > 0 && (
          <div className="mt-12">
            <h3 className="text-xl font-semibold mb-2">Minhas Avaliações</h3>
            <ul className="space-y-2">
              {avaliacoes.map((a, i) => (
                <li key={i} className="border rounded p-3 bg-white shadow-sm">
                  <p><strong>Data:</strong> {new Date(a.data_avaliacao).toLocaleDateString("pt-BR")}</p>
                  <p><strong>IMC:</strong> {a.imc} | <strong>% Gordura:</strong> {a.percentual_gordura}%</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
}
