// src/pages/Administrador/BackupsAdmin.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function BackupsAdmin() {
  const [backups, setBackups] = useState([]);
  const [erro, setErro] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const tipo = localStorage.getItem("perfil_tipo");
    if (tipo !== "admin") {
      navigate("/login");
    }
  }, [navigate]);

  async function carregarBackups() {
    try {
      const res = await api.get("/admin/backups");
      setBackups(res.data);
    } catch (err) {
      console.error("Erro ao carregar backups:", err);
      setErro("Erro ao carregar backups");
    }
  }

  useEffect(() => {
    carregarBackups();
  }, []);

  async function criarBackup() {
    setLoading(true);
    try {
      await api.post("/admin/backups");
      await carregarBackups();
    } catch (err) {
      setErro("Erro ao criar backup");
    } finally {
      setLoading(false);
    }
  }

  async function restaurarBackup(nome) {
    const confirm = window.confirm(`Deseja restaurar o backup: ${nome}? Isso sobrescreverá os dados atuais.`);
    if (!confirm) return;
    try {
      await api.post(`/admin/backups/${nome}/restaurar`);
      alert("Backup restaurado com sucesso.");
    } catch (err) {
      alert("Erro ao restaurar backup.");
    }
  }

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Backups do Sistema</h1>

        {erro && <p className="text-red-500 mb-4">{erro}</p>}

        <button
          onClick={criarBackup}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mb-6"
        >
          {loading ? "Criando..." : "Criar Backup"}
        </button>

        <div className="overflow-x-auto">
          <table className="w-full table-auto border border-gray-300 text-sm">
            <thead className="bg-gray-100 text-left">
              <tr>
                <th className="p-3">Nome do Arquivo</th>
                <th className="p-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {backups.map((nome, index) => (
                <tr key={index} className="border-t border-gray-200">
                  <td className="p-3 font-mono">{nome}</td>
                  <td className="p-3 space-x-2">
                    <a
                      href={`http://localhost:5000/admin/backups/${nome}`}
                      className="text-blue-600 hover:underline"
                      download
                    >
                      Baixar
                    </a>
                    <button
                      onClick={() => restaurarBackup(nome)}
                      className="text-red-600 hover:underline"
                    >
                      Restaurar
                    </button>
                  </td>
                </tr>
              ))}
              {backups.length === 0 && (
                <tr>
                  <td className="p-3 text-gray-500" colSpan="2">Nenhum backup encontrado.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
