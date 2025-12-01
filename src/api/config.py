import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Unified config loader supporting:
    1. APP_CONFIG env var (Cloud Run from Secret Manager)
    2. app-config.json file (local dev)
    3. .env file vars (fallback)
    """
    
    def __init__(self):
        load_dotenv()
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load config with priority chain"""
        
        # Priority 1: APP_CONFIG env var (Cloud Run)
        app_config_str = os.getenv("APP_CONFIG")
        if app_config_str and app_config_str != "{}":
            try:
                config = json.loads(app_config_str)
                logger.info("✓ Loaded config from APP_CONFIG (Cloud Run)")
                return config
            except json.JSONDecodeError as e:
                logger.warning(f"⚠ APP_CONFIG is not valid JSON: {e}")
        
        # Priority 2: app-config.json file (local dev)
        config_json_path = Path(__file__).parent / "app-config.json"
        if config_json_path.exists():
            try:
                with open(config_json_path) as f:
                    config = json.load(f)
                    logger.info(f"✓ Loaded config from {config_json_path} (Local)")
                    return config
            except json.JSONDecodeError as e:
                logger.warning(f"⚠ app-config.json is not valid JSON: {e}")
        
        # Priority 3: .env file vars (fallback)
        config = {
            "database_url": os.getenv("database_url"),
            "google_api_key": os.getenv("google_api_key"),
            "mcp_server_api_key": os.getenv("mcp_server_api_key"),
            "db_host": os.getenv("db_host"),
            "db_port": os.getenv("db_port"),
            "db_name": os.getenv("db_name"),
            "db_user": os.getenv("db_user"),
            "db_password": os.getenv("db_password"),
            "mcp_host":os.getenv("mcp_host"),
            "mcp_port":os.getenv("mcp_port"),
            "mcp_server_url": os.getenv("mcp_server_url"),
        }
        logger.info("✓ Loaded config from .env vars (Fallback)")
        return config
    
    @property
    def database_url(self) -> str:
        return self._config.get("database_url")
    
    @property
    def google_api_key(self) -> str:
        return self._config.get("google_api_key")
    
    @property
    def mcp_server_api_key(self) -> str:
        return self._config.get("mcp_server_api_key")
    
    @property
    def db_host(self) -> str:
        return self._config.get("db_host")
    
    @property
    def db_port(self) -> int:
        return int(self._config.get("db_port", 5432))
    
    @property
    def db_name(self) -> str:
        return self._config.get("db_name")
    
    @property
    def db_user(self) -> str:
        return self._config.get("db_user")
    
    @property
    def db_password(self) -> str:
        return self._config.get("db_password")
    
    @property
    def mcp_host(self) -> str:
        return self._config.get("mcp_host")
    
    @property
    def mcp_port(self) -> str:
        return self._config.get("mcp_port")
    
    @property
    def mcp_server_url(self) -> str:
        return self._config.get("mcp_server_url")

    @property
    def raw(self) -> dict:
        """Return raw config dict"""
        return self._config
    
    def get(self, key: str, default=None):
        """Get config value by key"""
        return self._config.get(key, default)
    
    def __repr__(self):
        return f"<Config: {list(self._config.keys())}>"


# Initialize config singleton
config = Config()