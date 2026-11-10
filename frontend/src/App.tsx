import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { LoginPage } from "./pages/auth/LoginPage";
import { OperacionesLayout } from "./layout/OperacionesLayout";

// Carga diferida (GSF: eficiencia de carbono/energía): cada pantalla es su propio trozo de código, que solo se descarga al
// entrar a ella. Así el login no baja Leaflet ni las pantallas de operaciones. Las páginas exportan por nombre, de ahí el `.then`.
const MapaPage = lazy(() => import("./pages/operaciones/MapaPage").then((m) => ({ default: m.MapaPage })));
const FlotaPage = lazy(() => import("./pages/operaciones/FlotaPage").then((m) => ({ default: m.FlotaPage })));
const ConductoresPage = lazy(() => import("./pages/operaciones/ConductoresPage").then((m) => ({ default: m.ConductoresPage })));
const ClientesPage = lazy(() => import("./pages/operaciones/ClientesPage").then((m) => ({ default: m.ClientesPage })));
const RutasPage = lazy(() => import("./pages/operaciones/RutasPage").then((m) => ({ default: m.RutasPage })));
const PedidosPage = lazy(() => import("./pages/operaciones/PedidosPage").then((m) => ({ default: m.PedidosPage })));
const SostenibilidadPage = lazy(() => import("./pages/operaciones/SostenibilidadPage").then((m) => ({ default: m.SostenibilidadPage })));
const SeguridadPage = lazy(() => import("./pages/operaciones/SeguridadPage").then((m) => ({ default: m.SeguridadPage })));
const ConductorPage = lazy(() => import("./pages/conductor/ConductorPage").then((m) => ({ default: m.ConductorPage })));

function PantallaCargando() {
  return (
    <main
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
    </main>
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
      <Suspense fallback={<PantallaCargando />}>
        <Routes>
          <Route path="*" element={<ConductorPage />} />
        </Routes>
      </Suspense>
    );
  }

  return (
    <Routes>
      <Route path="/app" element={<OperacionesLayout />}>
        <Route index element={<Navigate to="mapa" replace />} />
        <Route path="mapa" element={<MapaPage />} />
        {usuario.rolNombre === "ADMINISTRADOR" && <Route path="flota" element={<FlotaPage />} />}
        {usuario.rolNombre === "ADMINISTRADOR" && <Route path="conductores" element={<ConductoresPage />} />}
        <Route path="clientes" element={<ClientesPage />} />
        <Route path="rutas" element={<RutasPage />} />
        <Route path="pedidos" element={<PedidosPage />} />
        {usuario.rolNombre === "ADMINISTRADOR" && <Route path="sostenibilidad" element={<SostenibilidadPage />} />}
        <Route path="seguridad" element={<SeguridadPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/app/mapa" replace />} />
    </Routes>
  );
}
