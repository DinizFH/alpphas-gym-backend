import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../../components/Layout";
import api from "../../axios";

export default function LogsAdmin() {
  const [logs, setLogs] = useState([]);
  const [erro, setErro] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const tipo = localStorage.getItem("perfil_tipo");
    if (tipo !== "administrador") {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    async function carregarLogs() {
      try {
        const res = await api.get("/admin/logs");
        setLogs(res.data || []);
      } catch (err) {
        console.error("Erro ao carregar logs:", err);
        setErro("Erro ao carregar logs");
      }
    }
    carregarLogs();
  }, []);

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Logs do Sistema</h1>

        {erro && <p className="text-red-500">{erro}</p>}

        {logs.length === 0 ? (
          <p className="text-gray-600">Nenhum log registrado.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full table-auto border border-gray-300 text-sm">
              <thead className="bg-gray-100 text-left">
                <tr>
                  <th className="p-3">Data</th>
                  <th className="p-3">Usuário</th>
                  <th className="p-3">Ação</th>
                  <th className="p-3">Detalhes</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index} className="border-t border-gray-200">
                    <td className="p-3">
                      {log.data
                        ? new Date(log.data).toLocaleString()
                        : "—"}
                    </td>
                    <td className="p-3">{log.usuario || "—"}</td>
                    <td className="p-3">{log.acao || "—"}</td>
                    <td className="p-3">{log.detalhes || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
