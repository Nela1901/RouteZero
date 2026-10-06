import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { LoginPage } from "./pages/auth/LoginPage";
import { OperacionesLayout } from "./layout/OperacionesLayout";
import { MapaPage } from "./pages/operaciones/MapaPage";
import { FlotaPage } from "./pages/operaciones/FlotaPage";
import { ConductoresPage } from "./pages/operaciones/ConductoresPage";
import { PedidosPage } from "./pages/operaciones/PedidosPage";
import { SeguridadPage } from "./pages/operaciones/SeguridadPage";
import { ConductorPage } from "./pages/conductor/ConductorPage";

function PantallaCargando() {
  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--rz-bg)",
        color: "var(--rz-text-muted)",
      }}
    >
      Cargando…
    </div>
  );
}

export default function App() {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return <PantallaCargando />;
  }

  if (!usuario) {
    return (
      <Routes>
        <Route path="*" element={<LoginPage />} />
      </Routes>
    );
  }

  if (usuario.rolNombre === "CONDUCTOR") {
    return (
      <Routes>
        <Route path="*" element={<ConductorPage />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/app" element={<OperacionesLayout />}>
        <Route index element={<Navigate to="mapa" replace />} />
        <Route path="mapa" element={<MapaPage />} />
        {usuario.rolNombre === "ADMINISTRADOR" && <Route path="flota" element={<FlotaPage />} />}
        {usuario.rolNombre === "ADMINISTRADOR" && <Route path="conductores" element={<ConductoresPage />} />}
        <Route path="pedidos" element={<PedidosPage />} />
        <Route path="seguridad" element={<SeguridadPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/app/mapa" replace />} />
    </Routes>
  );
}
