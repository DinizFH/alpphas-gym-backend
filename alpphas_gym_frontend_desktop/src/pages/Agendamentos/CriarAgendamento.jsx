import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Select from "react-select";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function CriarAgendamento({ isEditMode = false }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const [tipoUsuario, setTipoUsuario] = useState("");
  const [alunos, setAlunos] = useState([]);
  const [alunoSelecionado, setAlunoSelecionado] = useState(null);
  const [form, setForm] = useState({
    tipo_agendamento: "",
    data_hora_inicio: "",
    data_hora_fim: "",
  });

  useEffect(() => {
    async function fetchDados() {
      try {
        const perfil = await api.get("/usuarios/perfil");
        setTipoUsuario(perfil.data.tipo_usuario);

        if (perfil.data.tipo_usuario !== "personal" && perfil.data.tipo_usuario !== "nutricionista") {
          alert("Acesso negado.");
          navigate("/dashboard/" + perfil.data.tipo_usuario);
          return;
        }

        const res = await api.get("/usuarios?tipo=aluno");
        const opcoes = res.data.map((aluno) => ({
          value: aluno.id_usuario,
          label: aluno.nome,
          cpf: aluno.cpf,
        }));
        setAlunos(opcoes);

        if (isEditMode && id) {
          const agendamentoRes = await api.get(`/agendamentos/${id}`);
          const ag = agendamentoRes.data;

          setForm({
            tipo_agendamento: ag.tipo_agendamento,
            data_hora_inicio: ag.data_hora_inicio.slice(0, 16),
            data_hora_fim: ag.data_hora_fim.slice(0, 16),
          });

          const aluno = opcoes.find((a) => a.value === ag.id_aluno);
          if (aluno) setAlunoSelecionado(aluno);
        }
      } catch (err) {
        console.error("Erro ao carregar dados:", err);
        alert("Erro ao carregar dados.");
      }
    }

    fetchDados();
  }, [id, isEditMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!alunoSelecionado) return alert("Selecione um aluno");

    const payload = {
      id_aluno: alunoSelecionado.value,
      tipo_agendamento: form.tipo_agendamento,
      data_hora_inicio: form.data_hora_inicio,
      data_hora_fim: form.data_hora_fim,
    };

    try {
      if (isEditMode) {
        await api.put(`/agendamentos/${id}`, {
          ...payload,
          status: "marcado", // ✅ garante persistência
        });
        alert("Agendamento atualizado com sucesso!");
      } else {
        await api.post("/agendamentos/", payload);
        alert("Agendamento criado com sucesso!");
      }
      navigate("/agendamentos");
    } catch (err) {
      console.error("Erro ao salvar:", err);
      alert("Erro ao salvar agendamento.");
    }
  };

  return (
    <Layout>
      <div className="p-6 max-w-2xl mx-auto bg-white rounded shadow">
        <h1 className="text-2xl font-bold mb-6">
          {isEditMode ? "Editar Agendamento" : "Novo Agendamento"}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-1">Aluno</label>
            <Select
              options={alunos}
              value={alunoSelecionado}
              onChange={(selected) => setAlunoSelecionado(selected)}
              placeholder="Buscar aluno pelo nome..."
              isDisabled={isEditMode}
            />
          </div>

          {alunoSelecionado && (
            <div>
              <label className="block text-sm font-semibold mt-2">CPF do aluno</label>
              <input
                type="text"
                value={alunoSelecionado.cpf || "Não informado"}
                disabled
                className="w-full p-2 border border-gray-300 rounded bg-gray-100"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold">Tipo de Agendamento</label>
            <select
              name="tipo_agendamento"
              value={form.tipo_agendamento}
              onChange={(e) => setForm({ ...form, tipo_agendamento: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded"
              required
            >
              <option value="">Selecione o tipo de agendamento</option>
              {tipoUsuario === "nutricionista" && (
                <>
                  <option value="Consulta">Consulta</option>
                  <option value="Avaliação">Avaliação</option>
                </>
              )}
              {tipoUsuario === "personal" && (
                <>
                  <option value="Avaliação">Avaliação</option>
                  <option value="Treino">Treino</option>
                </>
              )}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold">Data e Hora de Início</label>
            <input
              type="datetime-local"
              name="data_hora_inicio"
              value={form.data_hora_inicio}
              onChange={(e) => setForm({ ...form, data_hora_inicio: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold">Data e Hora de Término</label>
            <input
              type="datetime-local"
              name="data_hora_fim"
              value={form.data_hora_fim}
              onChange={(e) => setForm({ ...form, data_hora_fim: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
          >
            {isEditMode ? "Salvar Alterações" : "Criar Agendamento"}
          </button>
        </form>
      </div>
    </Layout>
  );
}
