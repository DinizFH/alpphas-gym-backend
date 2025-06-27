import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../../axios";
import logo from "../../assets/alpphas_logo.png";

export default function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({ email: "", senha: "" });
  const [erro, setErro] = useState("");

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");

    try {
      const res = await api.post("/auth/login", formData);
      const token = res.data.access_token;
      localStorage.setItem("token", token);

      // Buscar dados do perfil
      const perfilRes = await api.get("/usuarios/perfil");
      const { perfil_completo, tipo_usuario, email, nome, foto_perfil } = perfilRes.data;

      // Armazenar dados no localStorage
      localStorage.setItem("perfil_nome", nome);
      localStorage.setItem("perfil_tipo", tipo_usuario);
      localStorage.setItem("perfil_foto", foto_perfil || "");
      localStorage.setItem("perfil_email", email);

      // Redirecionar admin para o painel administrativo
      if (email === "administrador@alpphasgym.com") {
        navigate("/admin");
        return;
      }

      // Redirecionar usuários comuns
      if (!perfil_completo) {
        navigate("/completar-perfil");
      } else {
        navigate(`/dashboard/${tipo_usuario}`);
      }
    } catch (err) {
      const msg = err.response?.data?.msg || "Erro ao fazer login.";
      setErro(msg);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="flex justify-center mb-6">
          <img src={logo} alt="Logo Alpphas GYM" className="h-56" />
        </div>
        <h2 className="text-2xl font-semibold text-center mb-4">Entrar</h2>

        {erro && <p className="text-red-500 text-sm mb-2">{erro}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            name="email"
            placeholder="E-mail"
            value={formData.email}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <input
            type="password"
            name="senha"
            placeholder="Senha"
            value={formData.senha}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition"
          >
            Entrar
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Não tem uma conta?{" "}
          <Link to="/register" className="text-blue-600 hover:underline">
            Cadastre-se
          </Link>
        </p>
      </div>
    </div>
  );
}
