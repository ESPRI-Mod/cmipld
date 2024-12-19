from esgvoc.core.service.settings import ServiceSettings
from esgvoc.core.service.state import StateService
from pathlib import Path

settings_path = Path(__file__).parent / "settings.toml"
service_settings = ServiceSettings.load_from_file(str(settings_path))
state_service = StateService(service_settings)

