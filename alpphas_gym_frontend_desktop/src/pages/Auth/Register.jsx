import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../axios";
import logo from "../../assets/alpphas_logo.png";

export default function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    nome: "",
    email: "",
    senha: "",
    tipo_usuario: "aluno",
    cref: "",
    crn: "",
  });

  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");
    setSucesso("");

    const payload = {
      nome: formData.nome,
      email: formData.email,
      senha: formData.senha,
      tipo_usuario: formData.tipo_usuario,
    };

    if (formData.tipo_usuario === "personal") {
      payload.cref = formData.cref;
    } else if (formData.tipo_usuario === "nutricionista") {
      payload.crn = formData.crn;
    }

    try {
      const response = await api.post("/auth/register", payload);
      if (response.status === 201 || response.status === 200) {
        setSucesso("Cadastro realizado com sucesso!");
        setTimeout(() => navigate("/login"), 1500);
      }
    } catch (error) {
      const msg =
        error.response?.data?.msg || "Erro ao tentar registrar. Tente novamente.";
      setErro(msg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="flex justify-center mb-6">
          <img src={logo} alt="Logo Alpphas GYM" className="h-16" />
        </div>
        <h2 className="text-2xl font-semibold text-center mb-4">Crie sua conta</h2>

        {erro && <p className="text-red-500 text-sm mb-2">{erro}</p>}
        {sucesso && <p className="text-green-600 text-sm mb-2">{sucesso}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            name="nome"
            placeholder="Nome completo"
            value={formData.nome}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />
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
            placeholder="Senha (mín. 6 caracteres)"
            value={formData.senha}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <select
            name="tipo_usuario"
            value={formData.tipo_usuario}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="aluno">Aluno</option>
            <option value="personal">Personal</option>
            <option value="nutricionista">Nutricionista</option>
          </select>

          {/* Campo extra de acordo com o tipo de usuário */}
          {formData.tipo_usuario === "personal" && (
            <input
              type="text"
              name="cref"
              placeholder="CREF"
              value={formData.cref}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded"
              required
            />
          )}
          {formData.tipo_usuario === "nutricionista" && (
            <input
              type="text"
              name="crn"
              placeholder="CRN"
              value={formData.crn}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded"
              required
            />
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition"
          >
            Registrar
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Já tem uma conta?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
