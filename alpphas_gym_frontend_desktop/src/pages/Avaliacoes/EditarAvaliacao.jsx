import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../axios";
import Layout from "../../components/Layout";

export default function EditarAvaliacao() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({});
  const [usuario, setUsuario] = useState(null);
  const [erro, setErro] = useState("");

  const camposEsperados = [
    "altura", "peso", "idade",
    "dobra_peitoral", "dobra_triceps", "dobra_subescapular",
    "dobra_biceps", "dobra_axilar_media", "dobra_supra_iliaca",
    "pescoco", "ombro", "torax", "cintura", "abdomen", "quadril",
    "braco_direito", "braco_esquerdo", "braco_d_contraido", "braco_e_contraido",
    "antebraco_direito", "antebraco_esquerdo", "coxa_direita", "coxa_esquerda",
    "panturrilha_direita", "panturrilha_esquerda", "observacoes"
  ];

  useEffect(() => {
    async function fetchData() {
      try {
        const resPerfil = await api.get("/usuarios/perfil");
        setUsuario(resPerfil.data);

        if (resPerfil.data.tipo_usuario === "aluno") {
          navigate("/avaliacoes");
          return;
        }

        const res = await api.get(`/avaliacoes/${id}`);
        const dados = res.data;

        const normalizado = {};
        camposEsperados.forEach((campo) => {
          normalizado[campo] = dados[campo] ?? "";
        });

        setFormData(normalizado);
      } catch (err) {
        console.error("Erro ao carregar avaliação", err);
        setErro("Erro ao carregar os dados.");
      }
    }
    fetchData();
  }, [id, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const num = parseFloat(value.replace(",", "."));
    setFormData((prev) => ({
      ...prev,
      [name]: isNaN(num) ? "" : num
    }));
  };

  const calcularCampos = (dados) => {
    const peso = parseFloat(dados.peso) || 0;
    const altura = parseFloat(dados.altura) || 0;
    const idade = parseInt(dados.idade) || 0;
    const somaDobras =
      (parseFloat(dados.dobra_peitoral) || 0) +
      (parseFloat(dados.dobra_triceps) || 0) +
      (parseFloat(dados.dobra_subescapular) || 0) +
      (parseFloat(dados.dobra_biceps) || 0) +
      (parseFloat(dados.dobra_axilar_media) || 0) +
      (parseFloat(dados.dobra_supra_iliaca) || 0);

    const imc = altura ? (peso / (altura * altura)).toFixed(2) : 0;
    const densidade =
      1.10938 - 0.0008267 * somaDobras + 0.0000016 * Math.pow(somaDobras, 2) - 0.0002574 * idade;
    const percentual_gordura = (495 / densidade - 450).toFixed(2);
    const massa_gorda = ((peso * percentual_gordura) / 100).toFixed(2);
    const massa_magra = (peso - massa_gorda).toFixed(2);

    return {
      imc,
      percentual_gordura,
      massa_gorda,
      massa_magra
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const calculados = calcularCampos(formData);

    try {
      const payload = {
        ...formData,
        ...calculados,
      };

      Object.keys(payload).forEach((key) => {
        if (payload[key] === "") {
          payload[key] = null;
        }
      });

      await api.put(`/avaliacoes/${id}`, payload);
      navigate(`/avaliacoes/${id}`);
    } catch (err) {
      console.error("Erro ao atualizar avaliação", err);
      setErro("Erro ao salvar alterações.");
    }
  };

  if (!formData || !usuario) return <div>Carregando...</div>;

  return (
    <Layout>
      <div className="max-w-4xl mx-auto bg-white p-8 shadow-md rounded mt-6">
        <h2 className="text-2xl font-bold mb-4">Editar Avaliação Física</h2>
        {erro && <p className="text-red-600 mb-4">{erro}</p>}

        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-2">Dados Básicos</h3>
          </div>

          <InputField label="Altura (m)" name="altura" value={formData.altura} onChange={handleChange} />
          <InputField label="Peso (kg)" name="peso" value={formData.peso} onChange={handleChange} />
          <InputField label="Idade (anos)" name="idade" value={formData.idade} onChange={handleChange} />

          <div className="col-span-2 mt-4">
            <h3 className="text-lg font-semibold mb-2">Dobras Cutâneas (mm)</h3>
          </div>

          {[["Peitoral", "dobra_peitoral"],
            ["Tríceps", "dobra_triceps"],
            ["Subescapular", "dobra_subescapular"],
            ["Bíceps", "dobra_biceps"],
            ["Axilar Média", "dobra_axilar_media"],
            ["Supra-ilíaca", "dobra_supra_iliaca"]
          ].map(([label, name]) => (
            <InputField key={name} label={`Dobra ${label}`} name={name} value={formData[name]} onChange={handleChange} />
          ))}

          <div className="col-span-2 mt-4">
            <h3 className="text-lg font-semibold mb-2">Perimetrias (cm)</h3>
          </div>

          {[["Pescoço", "pescoco"],
            ["Ombro", "ombro"],
            ["Tórax", "torax"],
            ["Cintura", "cintura"],
            ["Abdômen", "abdomen"],
            ["Quadril", "quadril"],
            ["Braço Direito", "braco_direito"],
            ["Braço Esquerdo", "braco_esquerdo"],
            ["Braço Direito Contraído", "braco_d_contraido"],
            ["Braço Esquerdo Contraído", "braco_e_contraido"],
            ["Antebraço Direito", "antebraco_direito"],
            ["Antebraço Esquerdo", "antebraco_esquerdo"],
            ["Coxa Direita", "coxa_direita"],
            ["Coxa Esquerda", "coxa_esquerda"],
            ["Panturrilha Direita", "panturrilha_direita"],
            ["Panturrilha Esquerda", "panturrilha_esquerda"]
          ].map(([label, name]) => (
            <InputField key={name} label={label} name={name} value={formData[name]} onChange={handleChange} />
          ))}

          <div className="col-span-2 mt-4">
            <label className="block text-sm font-medium">Observações</label>
            <textarea
              name="observacoes"
              rows={4}
              value={formData.observacoes || ""}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, observacoes: e.target.value }))
              }
              className="w-full border rounded px-2 py-1"
              placeholder="Ex: Aluno em processo de definição muscular."
            />
          </div>

          <div className="col-span-2 mt-6">
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
            >
              Salvar Alterações
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

function InputField({ label, name, value, onChange }) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium">{label}</label>
      <input
        type="number"
        name={name}
        step="0.01"
        value={value !== undefined ? value : ""}
        onChange={onChange}
        className="w-full border rounded px-2 py-1"
        placeholder="Ex: 35.5"
      />
    </div>
  );
}
