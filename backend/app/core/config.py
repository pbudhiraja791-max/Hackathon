import os

class Settings:
    PROJECT_NAME: str = "Fluxora"
    HEADLINE: str = "Smarter Energy for a Sustainable Tomorrow"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fluxora-super-secret-production-key-2026")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fluxora.db")
    
    # Tariffs (₹ / kWh)
    DEFAULT_CURRENCY: str = "INR"
    TARIFF_OFF_PEAK: float = 5.50   # 22:00 - 06:00
    TARIFF_NORMAL: float = 8.00     # 06:00 - 17:00, 21:00 - 22:00
    TARIFF_PEAK: float = 12.50      # 17:00 - 21:00 (Peak window)
    DEMAND_CHARGE_PER_KW: float = 350.0  # Monthly demand charge
    
    # Grid emission factor (kg CO2 per kWh in India average ~ 0.716)
    CO2_KG_PER_KWH: float = 0.716
    
    # Simulation settings
    SIMULATION_INTERVAL_SECONDS: int = 5
    DEMO_MODE: bool = True

settings = Settings()
