// src/pages/PlanosAlimentares/ModalEnviarPlano.jsx
import { FaWhatsapp, FaEnvelope, FaPaperPlane } from "react-icons/fa";
import api from "../../axios";

export default function ModalEnviarPlano({ idPlano, onClose }) {
  const enviar = async (tipo) => {
    try {
      if (tipo === "email") {
        await api.post(`/planos/${idPlano}/enviar`);
        alert("Plano enviado por e-mail com sucesso!");
      } else if (tipo === "whatsapp") {
        await api.post(`/planos/${idPlano}/enviar-whatsapp`);
        alert("Plano enviado via WhatsApp com sucesso!");
      } else if (tipo === "ambos") {
        await api.post(`/planos/${idPlano}/enviar`);
        await api.post(`/planos/${idPlano}/enviar-whatsapp`);
        alert("Plano enviado por e-mail e WhatsApp com sucesso!");
      }
      onClose();
    } catch (err) {
      console.error("Erro ao enviar plano:", err);
      alert("Erro ao enviar plano.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-4 text-gray-500 hover:text-gray-700 text-xl"
        >
          ×
        </button>

        <h2 className="text-2xl font-bold text-center mb-3">Enviar Plano Alimentar</h2>
        <p className="text-center text-gray-600 mb-6">
          Selecione como deseja enviar o plano.
        </p>

        <div className="flex justify-center gap-6">
          <button
            onClick={() => enviar("email")}
            className="flex flex-col items-center bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg transition"
          >
            <FaEnvelope size={28} />
            <span className="mt-2 text-sm">E-mail</span>
          </button>

          <button
            onClick={() => enviar("whatsapp")}
            className="flex flex-col items-center bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg transition"
          >
            <FaWhatsapp size={28} />
            <span className="mt-2 text-sm">WhatsApp</span>
          </button>

          <button
            onClick={() => enviar("ambos")}
            className="flex flex-col items-center bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg transition"
          >
            <FaPaperPlane size={28} />
            <span className="mt-2 text-sm">Ambos</span>
          </button>
        </div>
      </div>
    </div>
  );
}
