import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";
import DashboardAluno from "./pages/Dashboard/DashboardAluno";
import DashboardPersonal from "./pages/Dashboard/DashboardPersonal";
import DashboardNutricionista from "./pages/Dashboard/DashboardNutricionista";
import CompletarPerfil from "./pages/Perfil/CompletarPerfil";
import AgendamentosScreen from "./pages/Agendamentos/AgendamentosScreen";
import AgendamentosAluno from "./pages/Agendamentos/AgendamentosAluno";
import CriarAgendamento from "./pages/Agendamentos/CriarAgendamento";
import DetalhesAgendamento from "./pages/Agendamentos/DetalhesAgendamento";
import AvaliacoesScreen from "./pages/Avaliacoes/AvaliacoesScreen";
import CriarAvaliacao from "./pages/Avaliacoes/CriarAvaliacao";
import EditarAvaliacao from "./pages/Avaliacoes/EditarAvaliacao";
import DetalhesAvaliacao from "./pages/Avaliacoes/DetalhesAvaliacao";
import ProgressoScreen from "./pages/Progresso/ProgressoScreen";
import ProgressoScreenAluno from "./pages/Progresso/ProgressoScreenAluno";
import TreinosScreen from "./pages/Treinos/TreinosScreen";
import CriarTreino from "./pages/Treinos/CriarTreino";
import EditarTreino from "./pages/Treinos/EditarTreino";
import TreinosAluno from "./pages/Treinos/TreinosAluno";
import DetalhesTreino from "./pages/Treinos/DetalhesTreino";
import ExerciciosScreen from "./pages/Exercicios/ExerciciosScreen";
import CriarExercicio from "./pages/Exercicios/CriarExercicio";
import EditarExercicio from "./pages/Exercicios/EditarExercicio";
import DetalhesExercicio from "./pages/Exercicios/DetalhesExercicio";
import RegistrosTreinoScreen from "./pages/RegistrosTreino/RegistrosTreinoScreen";
import CriarRegistroTreino from "./pages/RegistrosTreino/CriarRegistroTreino";
import EditarRegistroTreino from "./pages/RegistrosTreino/EditarRegistroTreino";
import DetalhesRegistroTreino from "./pages/RegistrosTreino/DetalhesRegistroTreino";
import NotFound from "./pages/NotFound";
import PrivateRoute from "./components/PrivateRoute";
import Layout from "./components/Layout";
import PlanosScreen from "./pages/PlanosAlimentares/PlanosScreen";
import VerPlanoAlimentar from "./pages/PlanosAlimentares/VerPlanoAlimentar";
import EditarPlano from "./pages/PlanosAlimentares/EditarPlano";
import DashboardAdmin from "./pages/Administrador/DashboardAdmin";
import LogsAdmin from "./pages/Administrador/LogsAdmin";
import UsuariosAdmin from "./pages/Administrador/UsuariosAdmin";
import EstatisticasAdmin from "./pages/Administrador/EstatisticasAdmin";
import BackupsAdmin from "./pages/Administrador/BackupsAdmin";
import ConfigAdmin from "./pages/Administrador/ConfigAdmin";





export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Dashboards */}
      <Route path="/dashboard/aluno" element={<PrivateRoute><DashboardAluno /></PrivateRoute>} />
      <Route path="/dashboard/personal" element={<PrivateRoute><DashboardPersonal /></PrivateRoute>} />
      <Route path="/dashboard/nutricionista" element={<PrivateRoute><DashboardNutricionista /></PrivateRoute>} />

      {/* Admin */}
      <Route path="/admin" element={<PrivateRoute><DashboardAdmin /></PrivateRoute>} />
      <Route path="/admin/logs" element={<PrivateRoute><LogsAdmin /></PrivateRoute>} />
      <Route path="/admin/usuarios" element={<PrivateRoute><UsuariosAdmin /></PrivateRoute>} />

      {/* Perfil */}
      <Route path="/completar-perfil" element={<PrivateRoute><CompletarPerfil /></PrivateRoute>} />

      {/* Agendamentos */}
      <Route path="/agendamentos" element={<PrivateRoute><AgendamentosScreen /></PrivateRoute>} />
      <Route path="/agendamentos-aluno" element={<PrivateRoute><AgendamentosAluno /></PrivateRoute>} />
      <Route path="/agendamentos/novo" element={<PrivateRoute><CriarAgendamento /></PrivateRoute>} />
      <Route path="/agendamentos/:id" element={<PrivateRoute><DetalhesAgendamento /></PrivateRoute>} />
      <Route path="/agendamentos/:id/editar" element={<PrivateRoute><CriarAgendamento isEditMode={true} /></PrivateRoute>} />

      {/* Avaliações */}
      <Route path="/avaliacoes" element={<PrivateRoute><AvaliacoesScreen /></PrivateRoute>} />
      <Route path="/avaliacoes/nova" element={<PrivateRoute><CriarAvaliacao /></PrivateRoute>} />
      <Route path="/avaliacoes/:id" element={<PrivateRoute><DetalhesAvaliacao /></PrivateRoute>} />
      <Route path="/avaliacoes/:id/editar" element={<PrivateRoute><EditarAvaliacao /></PrivateRoute>} />

      {/* Progresso */}
      <Route path="/progresso" element={<PrivateRoute><ProgressoScreen /></PrivateRoute>} />
      <Route path="/progresso/aluno" element={<PrivateRoute><ProgressoScreenAluno /></PrivateRoute>} />

      {/* Treinos */}
      <Route path="/treinos" element={<PrivateRoute><TreinosScreen /></PrivateRoute>} />
      <Route path="/treinos/novo" element={<PrivateRoute><CriarTreino /></PrivateRoute>} />
      <Route path="/treinos/:id" element={<PrivateRoute><DetalhesTreino /></PrivateRoute>} />
      <Route path="/treinos/:id/editar" element={<PrivateRoute><EditarTreino /></PrivateRoute>} />
      <Route path="/treinos-aluno" element={<PrivateRoute><TreinosAluno /></PrivateRoute>} />

      {/* Exercícios */}
      <Route path="/exercicios" element={<PrivateRoute><ExerciciosScreen /></PrivateRoute>} />
      <Route path="/exercicios/novo" element={<PrivateRoute><CriarExercicio /></PrivateRoute>} />
      <Route path="/exercicios/:id" element={<PrivateRoute><DetalhesExercicio /></PrivateRoute>} />
      <Route path="/exercicios/editar/:id" element={<PrivateRoute><EditarExercicio /></PrivateRoute>} />

      {/* Registros de Treino */}
      <Route path="/registrostreino" element={<PrivateRoute><Layout><RegistrosTreinoScreen /></Layout></PrivateRoute>} />
      <Route path="/registrostreino/novo" element={<PrivateRoute><Layout><CriarRegistroTreino /></Layout></PrivateRoute>} />
      <Route path="/registrostreino/:id" element={<PrivateRoute><Layout><DetalhesRegistroTreino /></Layout></PrivateRoute>} />
      <Route path="/registrostreino/:id/editar" element={<PrivateRoute><Layout><EditarRegistroTreino /></Layout></PrivateRoute>} />

      {/* Planos Alimentares */}
      <Route path="/planos" element={<PlanosScreen />} />
      <Route path="/planos/:id" element={<VerPlanoAlimentar />} />
      <Route path="/planos/:id/editar" element={<EditarPlano />} />

      {/*Painel Administrativo*/}
      <Route path="/admin/estatisticas" element={<PrivateRoute><EstatisticasAdmin /></PrivateRoute>} />
      <Route path="/admin/backups" element={<BackupsAdmin />} />
      <Route path="/admin/config" element={<ConfigAdmin />} />


      {/* Fallback */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
