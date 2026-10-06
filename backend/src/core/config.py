from datetime import time
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str
    # Rol app_admin (BYPASSRLS): solo lo usan los jobs de mantenimiento, nunca la API web.
    database_admin_url: str = ""
    supabase_url: str
    supabase_anon_key: str
    frontend_origin: str

    # --- Motor de rutas (cambio add-motor-rutas). Todos tienen valor por defecto: no hace falta
    # --- declararlos en el .env ni en Render; se sobrescriben con la variable en mayúsculas.
    # Depósito de Andina Reparto S.A.C. (parque industrial de Huancayo, dentro de la zona RN-007).
    deposito_latitud: float = -12.043632
    deposito_longitud: float = -75.226373
    # Multiplica la velocidad base por tipo de vía (DS 033-2001-MTC art. 162) para reflejar tráfico y paradas.
    factor_velocidad_urbana: float = 0.6
    hora_inicio_jornada: time = time(8, 0)
    tiempo_atencion_min: int = 10
    # Presupuesto de tiempo del optimizador (RN-015: ≤ 45 s en total para 150 pedidos y 15 vehículos).
    optimizacion_tiempo_s: float = 30.0
    optimizacion_tiempo_max_s: float = 40.0


settings = Settings()
