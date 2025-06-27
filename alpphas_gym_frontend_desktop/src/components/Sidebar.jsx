import { Link, useNavigate } from "react-router-dom";
import { FiLogOut, FiUser, FiSettings } from "react-icons/fi";
import logo from "../assets/alpphas_logo.png";

export default function Sidebar() {
  const navigate = useNavigate();

  const nome = localStorage.getItem("perfil_nome");
  const tipo = localStorage.getItem("perfil_tipo");
  const foto = localStorage.getItem("perfil_foto");
  const perfilCompleto = !!nome;

  const handleLogout = () => {
    ["token", "perfil_nome", "perfil_tipo", "perfil_foto", "perfil_email"].forEach((chave) =>
      localStorage.removeItem(chave)
    );
    navigate("/login");
  };

  const getLinks = () => {
    if (!tipo) return [];

    const base = [{ to: tipo === "admin" ? "/admin" : `/dashboard/${tipo}`, label: "Dashboard" }];

    if (tipo === "admin") {
      return [
        ...base,
        { to: "/admin/usuarios", label: "Usuários" },
        { to: "/admin/estatisticas", label: "Estatísticas" },
        { to: "/admin/backups", label: "Back-ups" },
        { to: "/admin/config", label: "Configurações" },

      ];
    }

    if (tipo === "aluno") {
      return [
        ...base,
        { to: "/treinos-aluno", label: "Treinos" },
        { to: "/registrostreino", label: "Registros de Treino" },
        { to: "/planos", label: "Plano Alimentar" },
        { to: "/agendamentos-aluno", label: "Meus Agendamentos" },
        { to: "/progresso/aluno", label: "Progresso" },
      ];
    }

    if (tipo === "personal") {
      return [
        ...base,
        { to: "/avaliacoes", label: "Avaliações" },
        { to: "/agendamentos", label: "Agendamentos" },
        { to: "/treinos", label: "Treinos" },
        { to: "/exercicios", label: "Exercícios" },
        { to: "/registrostreino", label: "Registros de Treino" },
        { to: "/progresso", label: "Progresso" },
      ];
    }

    if (tipo === "nutricionista") {
      return [
        ...base,
        { to: "/avaliacoes", label: "Avaliações" },
        { to: "/agendamentos", label: "Agendamentos" },
        { to: "/planos", label: "Plano Alimentar" },
        { to: "/progresso", label: "Progresso" },
      ];
    }

    return base;
  };

  const links = getLinks();

  return (
    <div className="h-screen w-64 bg-white shadow-lg flex flex-col justify-between fixed">
      <div className="flex flex-col items-center px-4 pt-6">
        <img src={logo} alt="Logo" className="w-32 mb-8" />

        <div className="flex flex-col items-center mb-6">
          <img
            src={
              foto
                ? `http://localhost:5000/static/uploads/${foto}`
                : "/icons/avatar.png"
            }
            alt="Perfil"
            className="w-20 h-20 rounded-full object-cover border"
          />
          <p className="mt-2 text-sm font-semibold text-center">
            {nome || "Usuário"}
          </p>

          {tipo !== "admin" && (
            <Link
              to="/completar-perfil"
              className="text-xs text-blue-600 hover:underline mt-1 flex items-center gap-1"
            >
              <FiUser /> Editar perfil
            </Link>
          )}
        </div>

        {perfilCompleto && (
          <nav className="w-full flex flex-col gap-4 text-sm font-medium text-center">
            {links.map((link, index) => (
              <Link key={index} to={link.to} className="hover:text-blue-600">
                {link.label}
              </Link>
            ))}
          </nav>
        )}
      </div>

      <div className="px-4 pb-6">
        <button
          onClick={handleLogout}
          className="w-full text-red-500 hover:text-red-700 text-sm flex items-center justify-center gap-2"
        >
          <FiLogOut /> Sair
        </button>
      </div>
    </div>
  );
}
