// src/pages/Administrador/UsuariosAdmin.jsx
import { useEffect, useState } from "react";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function UsuariosAdmin() {
  const [usuarios, setUsuarios] = useState([]);
  const [filtro, setFiltro] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [idSelecionado, setIdSelecionado] = useState(null);
  const [mostrarModal, setMostrarModal] = useState(false);

  useEffect(() => {
    carregarUsuarios();
  }, []);

  const carregarUsuarios = async () => {
    try {
      const res = await api.get("/admin/usuarios");
      setUsuarios(res.data);
    } catch (err) {
      console.error("Erro ao carregar usuários:", err);
    }
  };

  const desativarUsuario = async (id) => {
    try {
      await api.delete(`/admin/usuarios/${id}`);
      carregarUsuarios();
    } catch (err) {
      console.error("Erro ao desativar usuário:", err);
    }
  };

  const abrirModalSenha = (id) => {
    setIdSelecionado(id);
    setNovaSenha("");
    setMostrarModal(true);
  };

  const redefinirSenha = async () => {
    try {
      await api.put(`/admin/usuarios/${idSelecionado}/senha`, {
        nova_senha: novaSenha,
      });
      setMostrarModal(false);
      alert("Senha atualizada com sucesso.");
    } catch (err) {
      console.error("Erro ao redefinir senha:", err);
      alert("Erro ao redefinir senha.");
    }
  };

  const usuariosFiltrados = usuarios.filter((u) =>
    filtro ? u.tipo_usuario === filtro : true
  );

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-semibold mb-4">Usuários do Sistema</h1>

        <div className="mb-4 flex gap-2">
          <select
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            className="border px-2 py-1 rounded"
          >
            <option value="">Todos</option>
            <option value="aluno">Alunos</option>
            <option value="personal">Personais</option>
            <option value="nutricionista">Nutricionistas</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Nome</th>
                <th className="px-4 py-2">E-mail</th>
                <th className="px-4 py-2">Tipo</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuariosFiltrados.map((usuario) => (
                <tr key={usuario.id} className="border-b">
                  <td className="px-4 py-2">{usuario.id}</td>
                  <td className="px-4 py-2">{usuario.nome}</td>
                  <td className="px-4 py-2">{usuario.email}</td>
                  <td className="px-4 py-2">{usuario.tipo_usuario}</td>
                  <td className="px-4 py-2">
                    {usuario.ativo ? "Ativo" : "Inativo"}
                  </td>
                  <td className="px-4 py-2 flex flex-col gap-1">
                    <button
                      onClick={() => desativarUsuario(usuario.id)}
                      className="text-red-600 hover:underline"
                    >
                      {usuario.ativo ? "Desativar" : "Inativo"}
                    </button>
                    <button
                      onClick={() => abrirModalSenha(usuario.id)}
                      className="text-blue-600 hover:underline"
                    >
                      Redefinir Senha
                    </button>
                  </td>
                </tr>
              ))}
              {usuariosFiltrados.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-4">
                    Nenhum usuário encontrado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de redefinição de senha */}
      {mostrarModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded p-6 w-96">
            <h2 className="text-lg font-semibold mb-4">Redefinir Senha</h2>
            <input
              type="password"
              placeholder="Nova senha"
              className="border px-3 py-2 w-full rounded mb-4"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setMostrarModal(false)}
                className="text-gray-600 hover:underline"
              >
                Cancelar
              </button>
              <button
                onClick={redefinirSenha}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
