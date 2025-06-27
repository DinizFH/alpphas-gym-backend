import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center">
      <h1 className="text-5xl font-bold mb-4">404</h1>
      <p className="text-xl mb-6">Página não encontrada</p>
      <Link to="/login" className="text-blue-600 underline">Voltar para o login</Link>
    </div>
  );
}
