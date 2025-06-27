import api from "../../axios";

const RegistroTreinoService = {
  listarMeusRegistros: async () => {
    const res = await api.get("/registrostreino/meus");
    return res.data;
  },

  listarTodosRegistros: async () => {
    const res = await api.get("/registrostreino/");
    return res.data;
  },

  buscarPorId: async (id_registro) => {
    const res = await api.get(`/registrostreino/${id_registro}`);
    return res.data;
  },

  criarRegistro: async (dados) => {
    const res = await api.post("/registrostreino/", dados);
    return res.data;
  },
};

export default RegistroTreinoService;
