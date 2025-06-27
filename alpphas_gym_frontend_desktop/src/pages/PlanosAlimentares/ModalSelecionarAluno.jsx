import { useEffect, useState } from "react";
import api from "../../axios";
import CriarPlano from "./CriarPlano";

export default function ModalSelecionarAluno({ onClose, onPlanoCriado }) {
  const [alunos, setAlunos] = useState([]);
  const [busca, setBusca] = useState("");
  const [alunoSelecionado, setAlunoSelecionado] = useState(null);

  useEffect(() => {
    async function carregarAlunos() {
      try {
        const res = await api.get("/usuarios/alunos");
        setAlunos(res.data);
      } catch (err) {
        console.error("Erro ao carregar alunos:", err);
      }
    }
    carregarAlunos();
  }, []);

  const alunosFiltrados = alunos.filter((aluno) =>
    aluno.nome.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded shadow-md w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {!alunoSelecionado ? (
          <>
            <h2 className="text-xl font-bold mb-4">Selecionar Aluno</h2>
            <input
              type="text"
              placeholder="Buscar aluno por nome"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-full p-2 border rounded mb-4"
            />

            <ul className="space-y-2">
              {alunosFiltrados.map((aluno) => (
                <li
                  key={aluno.id_usuario}
                  className="flex justify-between items-center border p-2 rounded hover:bg-gray-100"
                >
                  <div>
                    <p className="font-semibold">{aluno.nome}</p>
                    <p className="text-sm text-gray-600">CPF: {aluno.cpf}</p>
                  </div>
                  <button
                    onClick={() => setAlunoSelecionado(aluno)}
                    className="bg-blue-600 text-white px-3 py-1 rounded"
                  >
                    Iniciar Plano
                  </button>
                </li>
              ))}
            </ul>

            <div className="mt-6 text-right">
              <button
                onClick={onClose}
                className="text-gray-600 hover:text-black"
              >
                Cancelar
              </button>
            </div>
          </>
        ) : (
          <CriarPlano
            aluno={alunoSelecionado}
            onCancel={() => setAlunoSelecionado(null)}
            onClose={() => {
              if (onPlanoCriado) onPlanoCriado();
              onClose();
            }}
          />
        )}
      </div>
    </div>
  );
}
