from nicegui import ui

# Define a shared header for all pages
def header():
    with ui.header(elevated=True).classes('bg-primary text-white items-center'):
        ui.label('Zendesk Article Sync').classes('text-lg')
        ui.space()
        ui.link('Add Article', '/').classes('text-white')
        ui.link('View List', '/list').classes('text-white')
        ui.link('Settings', '/settings').classes('text-white')