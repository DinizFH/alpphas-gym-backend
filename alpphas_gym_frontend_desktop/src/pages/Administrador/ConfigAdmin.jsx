import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../../components/Layout";
import api from "../../axios";

export default function ConfigAdmin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    const tipo = localStorage.getItem("perfil_tipo");
    const emailLocal = localStorage.getItem("perfil_email");
    if (tipo !== "admin") navigate("/login");
    else setEmail(emailLocal);
  }, [navigate]);

  const handleRedefinirSenha = async (e) => {
    e.preventDefault();
    try {
      const res = await api.put(`/admin/usuarios/1/senha`, {
        nova_senha: novaSenha,
      });
      setMensagem(res.data.message);
      setErro("");
      setNovaSenha("");
    } catch (err) {
      console.error("Erro ao redefinir senha:", err);
      setErro("Erro ao redefinir senha");
      setMensagem("");
    }
  };

  return (
    <Layout>
      <div className="p-6 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Configurações do Sistema</h1>

        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-2">Informações do Administrador</h2>
          <p>Email de login: <strong>{email}</strong></p>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-2">Redefinir Senha do Admin</h2>
          <form onSubmit={handleRedefinirSenha} className="space-y-4">
            <input
              type="password"
              placeholder="Nova senha"
              className="border p-2 w-full rounded"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
              required
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Redefinir Senha
            </button>
            {mensagem && <p className="text-green-600">{mensagem}</p>}
            {erro && <p className="text-red-600">{erro}</p>}
          </form>
        </section>

        {/* Futuras configurações adicionais */}
        <section className="mt-12">
          <h2 className="text-lg font-semibold mb-2">Outras configurações</h2>
          <p className="text-gray-500">Em breve: parâmetros do sistema, integrações, backups automáticos, personalização visual, entre outros.</p>
        </section>
      </div>
    </Layout>
  );
}
