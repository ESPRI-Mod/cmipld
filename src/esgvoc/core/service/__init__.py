from esgvoc.core.service.settings import ServiceSettings
from esgvoc.core.service.state import StateService


settings_path = "src/cmipld/core/service/settings.toml"
service_settings = ServiceSettings.load_from_file(settings_path)
# Initialize StateService
state_service = StateService(service_settings)

# state_service.connect_db()
