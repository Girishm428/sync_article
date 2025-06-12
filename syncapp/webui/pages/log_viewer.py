from nicegui import ui
from syncapp.config.logfile import create_log_file
from syncapp.loggers.log_cli import setup_logger
import re
from syncapp.webui.pages.header import header

logger = setup_logger(__name__)

# -----------------
# Page 4: Log Viewer
# -----------------
@ui.page('/logs')
def log_viewer_page():
    """Create a log viewer page with filtering and search capabilities."""
    log_file = create_log_file()
    header()

    # Create the main container
    ui.add_head_html('<style>.large-textarea .q-field__control { height: 100% !important; resize: none !important; }</style>')
    with ui.card().classes('w-full h-screen bg-white flex flex-col'):
        ui.label('Log Viewer').classes('text-2xl mb-4')
        
        # Create filter controls
        with ui.row().classes('w-full mb-4'):
            # Log level filter
            log_levels = ['ALL', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            level_select = ui.select(log_levels, value='ALL').classes('w-32')
            
            # Search input
            search_input = ui.input(placeholder='Search logs...').classes('w-64')
            
            # Refresh button
            refresh_btn = ui.button('Refresh', icon='refresh').classes('w-32')
        
        # Create log display area with flex container
        with ui.column().classes('w-full h-full flex-1 overflow-hidden'):
            # log_display = ui.textarea().classes('w-full h-full large-textarea')
            log_display = ui.html('Loading logs...').classes('w-full h-full font-mono text-sm overflow-auto')
            # log_display.set_value('Loading logs...')
            
        def format_log_line(line):
            """Format a log line with colors based on log level."""
            try:
                # Parse the log line
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| ([^|]+) \| ([^|]+) \| (.+)', line)
                if match:
                    _, _, level, _ = match.groups()
                    level = level.strip()
                    
                    # Add color based on log level
                    if level == 'ERROR':
                        return f'<span class="text-red-500">{line}</span>'
                    elif level == 'WARNING':
                        return f'<span class="text-yellow-500">{line}</span>'
                    elif level == 'CRITICAL':
                        return f'<span class="text-red-700">{line}</span>'
                    elif level == 'INFO':
                        return f'<span class="text-black">{line}</span>'
                return line
            except:
                return line
        
        def load_logs():
            """Load and filter logs based on current settings."""
            try:
                if not log_file.exists():
                    log_display.set_value('No log file found.')
                    return
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Apply filters
                filtered_lines = []
                search_text = search_input.value.lower()
                selected_level = level_select.value
                
                for line in lines:
                    # Apply level filter
                    if selected_level != 'ALL' and f'| {selected_level} |' not in line:
                        continue
                    
                    # Apply search filter
                    if search_text and search_text not in line.lower():
                        continue
                    
                    filtered_lines.append(format_log_line(line))
                
                # Update display
                # log_display.set_value(''.join(filtered_lines))
                log_display.content = '<br>'.join(filtered_lines)
                
            except Exception as e:
                logger.error("Error loading logs: %s", str(e))
                log_display.set_value(f'Error loading logs: {str(e)}')
        
               
        # Set up event handlers
        level_select.on('update', load_logs)
        search_input.on('update', load_logs)
        refresh_btn.on('click', load_logs)
        
        # Initial load
        load_logs()
        
        # Auto-refresh every 5 seconds
        ui.timer(5.0, load_logs) 