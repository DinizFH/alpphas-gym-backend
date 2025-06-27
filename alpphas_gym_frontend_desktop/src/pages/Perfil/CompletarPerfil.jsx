import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../axios";

const listaPaises = [
  { nome: "Brasil", codigo: "+55" },
  { nome: "Portugal", codigo: "+351" },
  { nome: "Estados Unidos", codigo: "+1" },
];

export default function CompletarPerfil() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    cpf: "",
    data_nascimento: "",
    endereco: "",
    celular: "",
    whatsapp: "",
  });
  const [foto, setFoto] = useState(null);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  const [paisCel, setPaisCel] = useState("+55");
  const [dddCel, setDddCel] = useState("");
  const [numeroCel, setNumeroCel] = useState("");

  const [paisZap, setPaisZap] = useState("+55");
  const [dddZap, setDddZap] = useState("");
  const [numeroZap, setNumeroZap] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setFoto(e.target.files[0]);
  };

  const formatarNumero = (pais, ddd, numero) => {
    const dddLimpo = ddd.replace(/^0+/, "");
    const numeroLimpo = numero.replace(/\D/g, "");
    return `${pais}${dddLimpo}${numeroLimpo}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");
    setSucesso("");

    const form = new FormData();
    formData.celular = formatarNumero(paisCel, dddCel, numeroCel);
    formData.whatsapp = formatarNumero(paisZap, dddZap, numeroZap);

    Object.entries(formData).forEach(([key, value]) => form.append(key, value));
    if (foto) form.append("foto_perfil", foto);

    try {
      const res = await api.put("/usuarios/completar", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (res.status === 200) {
        setSucesso("Perfil completado com sucesso!");
        const perfil = await api.get("/usuarios/perfil");
        const tipo = perfil.data.tipo_usuario;
        navigate(`/dashboard/${tipo}`);
      }
    } catch (err) {
      const msg = err.response?.data?.msg || "Erro ao completar perfil.";
      setErro(msg);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-lg">
        <div className="flex justify-center mb-6">
          <img src="/src/assets/alpphas_logo.png" alt="Logo Alpphas GYM" className="h-56" />
        </div>
        <h2 className="text-2xl font-semibold text-center mb-6">Complete seu Perfil</h2>

        {erro && <p className="text-red-500 text-sm mb-2">{erro}</p>}
        {sucesso && <p className="text-green-600 text-sm mb-2">{sucesso}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full"
          />

          <input
            type="text"
            name="cpf"
            placeholder="CPF"
            value={formData.cpf}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <input
            type="date"
            name="data_nascimento"
            value={formData.data_nascimento}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <input
            type="text"
            name="endereco"
            placeholder="Endereço completo"
            value={formData.endereco}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />

          <div className="flex gap-2">
            <select
              value={paisCel}
              onChange={(e) => setPaisCel(e.target.value)}
              className="p-2 border border-gray-300 rounded w-1/4"
            >
              {listaPaises.map((pais) => (
                <option key={pais.codigo} value={pais.codigo}>{pais.nome} ({pais.codigo})</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="DDD"
              value={dddCel}
              onChange={(e) => setDddCel(e.target.value.replace(/\D/g, ""))}
              className="p-2 border border-gray-300 rounded w-1/4"
              required
            />
            <input
              type="text"
              placeholder="Número de Celular"
              value={numeroCel}
              onChange={(e) => setNumeroCel(e.target.value.replace(/\D/g, ""))}
              className="p-2 border border-gray-300 rounded w-1/2"
              required
            />
          </div>

          <div className="flex gap-2">
            <select
              value={paisZap}
              onChange={(e) => setPaisZap(e.target.value)}
              className="p-2 border border-gray-300 rounded w-1/4"
            >
              {listaPaises.map((pais) => (
                <option key={pais.codigo} value={pais.codigo}>{pais.nome} ({pais.codigo})</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="DDD"
              value={dddZap}
              onChange={(e) => setDddZap(e.target.value.replace(/\D/g, ""))}
              className="p-2 border border-gray-300 rounded w-1/4"
              required
            />
            <input
              type="text"
              placeholder="WhatsApp"
              value={numeroZap}
              onChange={(e) => setNumeroZap(e.target.value.replace(/\D/g, ""))}
              className="p-2 border border-gray-300 rounded w-1/2"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition"
          >
            Salvar
          </button>
        </form>
      </div>
    </div>
  );
}
