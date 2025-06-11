from nicegui import ui
from syncapp.webui.pages.header import header
from syncapp.config.settings import ensure_settings_file, load_settings, save_settings_to_file
from syncapp.loggers.log_cli import setup_logger

#------------ logger ------------
logger = setup_logger(__name__)

#------------ Settings ------------
SETTINGS_FILE = ensure_settings_file()

load_settings()


settings = load_settings()

# -----------------
# Page 3: Settings
# -----------------
@ui.page('/settings')
def settings_page():
    header()
    current_settings = load_settings()
    with ui.card().classes('w-full max-w-lg mx-auto mt-8'):
        ui.label('Settings').classes('text-h6')
        
        zendesk_domain = ui.input('Zendesk Domain', value=current_settings.get("ZENDESK_DOMAIN", "")).props('outlined')
        email = ui.input('Email', value=current_settings.get("EMAIL", "")).props('outlined')
        api_token = ui.input('API Token', value=current_settings.get("API_TOKEN", ""),password=True).classes('mb-4').props('outlined')
        locale = ui.input('Locale', value=current_settings.get("LOCAL", "en-us")).props('outlined')


        async def save_settings():
            if not all([zendesk_domain.value, email.value, api_token.value, locale.value]):
                ui.notify('All fields are required!', type='negative')
                return
            
            settings.update({
                "ZENDESK_DOMAIN": zendesk_domain.value,
                "EMAIL": email.value,
                "API_TOKEN": api_token.value,
                "LOCAL": locale.value,
            })
            save_settings_to_file(settings)
            ui.notify(f"Settings saved successfully!", type='positive')
            
            # Clear inputs
            zendesk_domain.value = ''
            email.value = ''
            api_token.value = ''
            locale.value = ''

        ui.button('Save Settings', on_click=save_settings).props('color=primary')
