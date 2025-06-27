import { useState, useEffect } from "react";
import api from "../../axios";
import Layout from "../../components/Layout";
import GraficoPizza from "../../components/GraficoPizza";
import GraficoBarras from "../../components/GraficoBarras";

export default function ProgressoScreen() {
  const [busca, setBusca] = useState("");
  const [resultados, setResultados] = useState([]);
  const [selecionado, setSelecionado] = useState(null);
  const [avaliacoes, setAvaliacoes] = useState([]);

  useEffect(() => {
    if (busca.length >= 2) {
      const delay = setTimeout(async () => {
        try {
          const res = await api.get(`/avaliacoes/buscar-aluno?nome=${busca}`);
          setResultados(res.data);
        } catch (err) {
          console.error("Erro ao buscar aluno", err);
        }
      }, 400);
      return () => clearTimeout(delay);
    }
  }, [busca]);

  const carregarEvolucao = async (id) => {
    try {
      const res = await api.get(`/avaliacoes/evolucao/${id}`);
      setSelecionado(res.data.aluno);
      setAvaliacoes(res.data.avaliacoes);
    } catch (err) {
      console.error("Erro ao carregar evolução", err);
    }
  };

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
        <h1 className="text-2xl font-bold mb-4">Progresso do Aluno</h1>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Buscar aluno por nome..."
            className="w-full border rounded px-3 py-2"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          {resultados.length > 0 && (
            <ul className="border mt-1 rounded max-h-40 overflow-y-auto">
              {resultados.map((aluno) => (
                <li
                  key={aluno.id_usuario}
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => {
                    carregarEvolucao(aluno.id_usuario);
                    setResultados([]);
                    setBusca("");
                  }}
                >
                  {aluno.nome} ({aluno.cpf})
                </li>
              ))}
            </ul>
          )}
        </div>

        {selecionado && (
          <div className="mb-6">
            <p><strong>Aluno:</strong> {selecionado.nome}</p>
            <p><strong>CPF:</strong> {selecionado.cpf}</p>
          </div>
        )}

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
            </ul>
          </div>
        )}

        {avaliacoes.length > 1 && (
          <div className="space-y-10">
            {["imc", "percentual_gordura", "massa_magra", "massa_gorda", "ombro", "torax", "cintura",
            "abdomen", "quadril", "braco_direito", "braco_esquerdo", "braco_d_contraido", "braco_e_contraido",
            "antebraco_direito", "antebraco_esquerdo", "coxa_direita", "coxa_esquerda",
            "panturrilha_direita", "panturrilha_esquerda"].map((campo) => (
              <GraficoBarras key={campo} avaliacoes={avaliacoes} campo={campo} />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
