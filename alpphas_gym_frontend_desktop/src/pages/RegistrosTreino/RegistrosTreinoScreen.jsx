import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import ModalSelecionarTreino from "./ModalSelecionarTreino";

export default function RegistrosTreinoScreen() {
  const [registros, setRegistros] = useState([]);
  const [filtro, setFiltro] = useState("");
  const [tipo, setTipo] = useState("");
  const [nomeUsuario, setNomeUsuario] = useState("");
  const [mostrarModal, setMostrarModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function carregarDados() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setTipo(perfil.data.tipo_usuario);
        setNomeUsuario(perfil.data.nome);

        const res = perfil.data.tipo_usuario === "aluno"
          ? await api.get("/registrostreino/meus")
          : await api.get("/registrostreino/");

        setRegistros(res.data);
      } catch (err) {
        console.error("Erro ao carregar registros:", err);
        alert("Erro ao carregar registros.");
      }
    }

    carregarDados();
  }, []);

  const registrosFiltrados = registros.filter((reg) =>
    tipo === "aluno"
      ? true
      : reg.nome_aluno?.toLowerCase().includes(filtro.toLowerCase())
  );

  const handleVerDetalhes = (id) => {
    navigate(`/registrostreino/${id}`);
  };

  const handleEditar = (id) => {
    navigate(`/registrostreino/${id}/editar`);
  };

  const handleExcluir = async (id) => {
    const confirmar = window.confirm("Tem certeza que deseja excluir este registro?");
    if (!confirmar) return;

    try {
      await api.delete(`/registrostreino/${id}`);
      setRegistros((prev) => prev.filter((r) => r.id_registro !== id));
    } catch (err) {
      console.error("Erro ao excluir registro:", err);
      alert("Erro ao excluir registro.");
    }
  };

  const handleSelecionarTreino = (dados) => {
    setMostrarModal(false);
    navigate("/registrostreino/novo", { state: dados });
  };

  const formatarDataHora = (data) =>
    new Date(data).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {tipo === "aluno"
            ? "Meus Registros de Treino"
            : "Registros de Treino dos Alunos"}
        </h1>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => setMostrarModal(true)}
        >
          Novo Registro de Treino
        </button>
      </div>

      {tipo !== "aluno" && (
        <input
          type="text"
          placeholder="Buscar aluno por nome..."
          className="mb-4 p-2 border border-gray-300 rounded w-full"
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
        />
      )}

      {registrosFiltrados.length === 0 ? (
        <p className="text-gray-500">Nenhum registro encontrado.</p>
      ) : (
        <div className="grid gap-4">
          {registrosFiltrados.map((registro) => (
            <div
              key={registro.id_registro}
              className="bg-white shadow rounded p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
            >
              <div>
                <p className="font-semibold">
                  {tipo === "aluno"
                    ? registro.nome_treino
                    : `${registro.nome_aluno} - ${registro.nome_treino}`}
                </p>
                <p className="text-gray-600">
                  Registrado em: {formatarDataHora(registro.data_execucao)}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  className="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
                  onClick={() => handleVerDetalhes(registro.id_registro)}
                >
                  Ver Detalhes
                </button>
                {(tipo === "aluno" || tipo === "personal") && (
                  <>
                    <button
                      className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600"
                      onClick={() => handleEditar(registro.id_registro)}
                    >
                      Editar
                    </button>
                    <button
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                      onClick={() => handleExcluir(registro.id_registro)}
                    >
                      Excluir
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {mostrarModal && (
        <ModalSelecionarTreino
          onClose={() => setMostrarModal(false)}
          onSelecionar={handleSelecionarTreino}
        />
      )}
    </div>
  );
}
