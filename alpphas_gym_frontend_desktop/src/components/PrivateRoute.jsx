import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import axios from "axios";

export default function PrivateRoute({ children }) {
  const [autenticado, setAutenticado] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const verificarToken = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setAutenticado(false);
        return;
      }

      try {
        const res = await axios.get("http://localhost:5000/usuarios/perfil", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const { nome, tipo_usuario, foto_perfil, email } = res.data;

        // Armazenar no localStorage
        localStorage.setItem("perfil_nome", nome);
        localStorage.setItem("perfil_tipo", tipo_usuario);
        localStorage.setItem("perfil_foto", foto_perfil || "");
        localStorage.setItem("perfil_email", email);

        // Verificação extra para rotas admin
        const rotaAdmin = location.pathname.startsWith("/admin");
        const ehAdmin = email === "administrador@alpphasgym.com";

        if (rotaAdmin && !ehAdmin) {
          setAutenticado(false);
        } else {
          setAutenticado(true);
        }

      } catch (err) {
        console.error("Erro ao verificar token:", err);
        setAutenticado(false);
      }
    };

    verificarToken();
  }, [location.pathname]);

  if (autenticado === null) {
    return (
      <div className="flex justify-center items-center h-screen text-gray-600">
        <p className="text-lg">Verificando autenticação...</p>
      </div>
    );
  }

  return autenticado ? children : <Navigate to="/login" replace />;
}
