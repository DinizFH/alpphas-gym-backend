import { useEffect, useState } from "react";
import api from "../../axios";

export default function ModalSelecionarTreino({ onClose, onSelecionar }) {
  const [tipo, setTipo] = useState("");
  const [alunoSelecionado, setAlunoSelecionado] = useState(null);
  const [alunos, setAlunos] = useState([]);
  const [treinos, setTreinos] = useState([]);
  const [busca, setBusca] = useState("");

  useEffect(() => {
    async function carregarPerfil() {
      try {
        const res = await api.get("/usuarios/perfil");
        setTipo(res.data.tipo_usuario);

        if (res.data.tipo_usuario === "aluno") {
          const treinosRes = await api.get("/treinos/aluno");
          setTreinos(treinosRes.data || []);
        } else if (res.data.tipo_usuario === "personal") {
          const alunosRes = await api.get("/usuarios/alunos");
          setAlunos(alunosRes.data || []);
        }
      } catch (err) {
        console.error("Erro ao carregar perfil:", err);
      }
    }

    carregarPerfil();
  }, []);

  async function carregarTreinosDoAluno(id_aluno) {
    try {
      const res = await api.get(`/treinos/aluno/${id_aluno}`);
      setTreinos(res.data || []);
    } catch (error) {
      console.error("Erro ao carregar treinos:", error);
    }
  }

  const handleSelecionarAluno = (aluno) => {
    setAlunoSelecionado(aluno);
    carregarTreinosDoAluno(aluno.id_usuario);
  };

  const alunosFiltrados = alunos.filter((a) =>
    a.nome.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded shadow w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">
          {tipo === "personal" && !alunoSelecionado
            ? "Selecionar Aluno"
            : "Selecionar Treino"}
        </h2>

        {tipo === "personal" && !alunoSelecionado && (
          <>
            <input
              type="text"
              className="w-full border border-gray-300 p-2 mb-4 rounded"
              placeholder="Buscar aluno por nome..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
            />
            {alunosFiltrados.map((aluno) => (
              <div
                key={aluno.id_usuario}
                className="p-2 border-b flex justify-between items-center hover:bg-gray-100 cursor-pointer"
                onClick={() => handleSelecionarAluno(aluno)}
              >
                <span>{aluno.nome}</span>
                <span className="text-sm text-gray-500">CPF: {aluno.cpf}</span>
              </div>
            ))}
          </>
        )}

        {(tipo === "aluno" || alunoSelecionado) && (
          <>
            {alunoSelecionado && (
              <div className="mb-4">
                <p className="font-semibold">
                  Aluno selecionado: {alunoSelecionado.nome}
                </p>
              </div>
            )}
            {treinos.length === 0 ? (
              <p className="text-gray-500">Nenhum treino encontrado.</p>
            ) : (
              <ul className="divide-y">
                {treinos.map((treino) => (
                  <li
                    key={treino.id_treino}
                    className="py-2 px-3 hover:bg-gray-100 cursor-pointer rounded"
                    onClick={() =>
                      onSelecionar({
                        id_treino: treino.id_treino,
                        id_aluno: alunoSelecionado?.id_usuario || null,
                        nome_treino: treino.nome_treino,
                      })
                    }
                  >
                    {treino.nome_treino}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        <div className="mt-6 text-right">
          <button
            onClick={onClose}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
