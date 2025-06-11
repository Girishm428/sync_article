import syncapp.config.database as db
from nicegui import ui
from datetime import datetime

def format_cron_schedule(cron_schedule):
    """Convert cron expression to user-friendly format."""
    if not cron_schedule:
        return 'Not scheduled'
    
    try:
        parts = cron_schedule.split()
        if len(parts) >= 6:
            minute = parts[1]
            hour = parts[2]
            day = parts[3]
            month = parts[4]
            weekday = parts[5]
            
            # Format time
            time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
            
            # Determine frequency
            if day == '*' and month == '*' and weekday == '*':
                return f"Daily at {time_str}"
            elif day == '*' and month == '*' and weekday == '0':
                return f"Weekly on Sunday at {time_str}"
            elif day == '1' and month == '*' and weekday == '*':
                return f"Monthly on 1st at {time_str}"
            else:
                return f"Custom: {cron_schedule}"
    except Exception:
        return cron_schedule

def create_cron_handler(article, refresh_callback):
    """
    Creates a cron handler for an article.
    
    Args:
        article (dict): The article data
        refresh_callback (callable): Function to refresh the UI after cron update
    """
    def handle_cron():
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-lg'):
            ui.label('Schedule Sync').classes('text-h5 q-mb-md')
            
            # Convert SQLite Row to dict for safe access
            article_dict = dict(article)
            
            # Current cron status
            current_cron = article_dict.get('cron_schedule', '')
            
            # Parse current schedule to determine frequency
            initial_frequency = 'Daily'
            initial_time = '00:00'
            if current_cron:
                ui.label(f'Current schedule: {current_cron}').classes('text-sm text-gray-500 mb-4')
                try:
                    # Parse cron expression
                    parts = current_cron.split()
                    if len(parts) >= 6:  # Standard cron format
                        hour = parts[2]
                        minute = parts[1]
                        day = parts[3]
                        month = parts[4]
                        weekday = parts[5]
                        
                        # Determine frequency based on cron pattern
                        if day == '*' and month == '*' and weekday == '*':
                            initial_frequency = 'Daily'
                        elif day == '*' and month == '*' and weekday == '0':
                            initial_frequency = 'Weekly'
                        elif day == '1' and month == '*' and weekday == '*':
                            initial_frequency = 'Monthly'
                        else:
                            initial_frequency = 'Custom'
                        
                        initial_time = f"{hour.zfill(2)}:{minute.zfill(2)}"
                except Exception:
                    # If parsing fails, default to Daily
                    initial_frequency = 'Daily'
                    initial_time = '00:00'
            
            # Frequency selection
            frequency = ui.select(
                ['Daily', 'Weekly', 'Monthly', 'Custom'],
                value=initial_frequency
            ).classes('w-full mb-4')
            
            # Time selection
            with ui.row().classes('w-full mb-4 gap-4'):
                ui.label('Time:').classes('text-sm')
                time = ui.time(value=initial_time).classes('w-32')
            
            # Custom cron input (hidden by default)
            custom_cron = ui.input(
                'Custom Cron Expression',
                value=current_cron if initial_frequency == 'Custom' else ''
            ).classes('w-full mb-4')
            custom_cron.visible = initial_frequency == 'Custom'
            
            # Show/hide custom cron input based on frequency selection
            def on_frequency_change(e):
                custom_cron.visible = e.value == 'Custom'
            frequency.on('update', on_frequency_change)
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: save_cron(
                    article_dict['id'],
                    frequency.value,
                    time.value,
                    custom_cron.value,
                    dialog
                )).props('flat color=primary')
        dialog.open()
    
    def save_cron(article_id, frequency, time, custom_cron, dialog):
        try:
            # Validate inputs
            if frequency == 'Custom' and not custom_cron.strip():
                ui.notify('Please enter a custom cron expression', type='negative')
                return
            
            # Format cron schedule
            if frequency == 'Custom':
                cron_schedule = custom_cron.strip()
            else:
                # Convert frequency to cron expression
                if frequency == 'Daily':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} * * *"
                elif frequency == 'Weekly':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} * * 0"
                elif frequency == 'Monthly':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} 1 * *"
            
            # Update database
            conn = db.get_db_connection()
            conn.execute("""
                UPDATE articles 
                SET cron_schedule = ?, last_cron_update = ?
                WHERE id = ?
            """, (cron_schedule, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_id))
            conn.commit()
            conn.close()
            
            ui.notify('Schedule updated successfully!', type='positive')
            dialog.close()
            refresh_callback()
        except Exception as e:
            ui.notify(f'Error updating schedule: {str(e)}', type='negative')
    
    return handle_cron

def create_bulk_cron_handler(selected_articles, refresh_callback):
    """
    Creates a bulk cron handler for multiple articles.
    
    Args:
        selected_articles (set): Set of selected article IDs
        refresh_callback (callable): Function to refresh the UI after cron update
    """
    def handle_bulk_cron():
        if not selected_articles:
            ui.notify('Please select at least one article to schedule', type='warning')
            return

        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-lg'):
            ui.label('Schedule Sync').classes('text-h5 q-mb-md')
            ui.label(f'Schedule sync for {len(selected_articles)} articles').classes('text-sm text-gray-500 mb-4')
            
            # Get current schedules for selected articles
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cron_schedule 
                FROM articles 
                WHERE id IN ({})
            """.format(','.join('?' * len(selected_articles))), list(selected_articles))
            
            current_schedules = [dict(row)['cron_schedule'] for row in cursor.fetchall()]
            conn.close()
            
            # Check if all articles have the same schedule
            unique_schedules = set(filter(None, current_schedules))
            if len(unique_schedules) == 1:
                current_cron = unique_schedules.pop()
                ui.label(f'Current schedule: {current_cron}').classes('text-sm text-gray-500 mb-4')
                
                # Parse current schedule to determine frequency
                initial_frequency = 'Daily'
                initial_time = '00:00'
                try:
                    # Parse cron expression
                    parts = current_cron.split()
                    if len(parts) >= 6:  # Standard cron format
                        hour = parts[2]
                        minute = parts[1]
                        day = parts[3]
                        month = parts[4]
                        weekday = parts[5]
                        
                        # Determine frequency based on cron pattern
                        if day == '*' and month == '*' and weekday == '*':
                            initial_frequency = 'Daily'
                        elif day == '*' and month == '*' and weekday == '0':
                            initial_frequency = 'Weekly'
                        elif day == '1' and month == '*' and weekday == '*':
                            initial_frequency = 'Monthly'
                        else:
                            initial_frequency = 'Custom'
                        
                        initial_time = f"{hour.zfill(2)}:{minute.zfill(2)}"
                except Exception:
                    # If parsing fails, default to Daily
                    initial_frequency = 'Daily'
                    initial_time = '00:00'
            else:
                initial_frequency = 'Daily'
                initial_time = '00:00'
                if unique_schedules:
                    ui.label('Note: Selected articles have different schedules').classes('text-sm text-yellow-500 mb-4')
            
            # Frequency selection
            frequency = ui.select(
                ['Daily', 'Weekly', 'Monthly', 'Custom'],
                value=initial_frequency
            ).classes('w-full mb-4')
            
            # Time selection
            with ui.row().classes('w-full mb-4 gap-4'):
                ui.label('Time:').classes('text-sm')
                time = ui.time(value=initial_time).classes('w-32')
            
            # Custom cron input (hidden by default)
            custom_cron = ui.input('Custom Cron Expression').classes('w-full mb-4')
            custom_cron.visible = initial_frequency == 'Custom'
            
            # Show/hide custom cron input based on frequency selection
            def on_frequency_change(e):
                custom_cron.visible = e.value == 'Custom'
            frequency.on('update', on_frequency_change)
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: save_bulk_cron(
                    list(selected_articles),
                    frequency.value,
                    time.value,
                    custom_cron.value,
                    dialog
                )).props('flat color=primary')
        dialog.open()
    
    def save_bulk_cron(article_ids, frequency, time, custom_cron, dialog):
        try:
            # Validate inputs
            if frequency == 'Custom' and not custom_cron.strip():
                ui.notify('Please enter a custom cron expression', type='negative')
                return
            
            # Format cron schedule
            if frequency == 'Custom':
                cron_schedule = custom_cron.strip()
            else:
                # Convert frequency to cron expression
                if frequency == 'Daily':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} * * *"
                elif frequency == 'Weekly':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} * * 0"
                elif frequency == 'Monthly':
                    cron_schedule = f"0 {time.split(':')[1]} {time.split(':')[0]} 1 * *"
            
            # Update database
            conn = db.get_db_connection()
            conn.execute("""
                UPDATE articles 
                SET cron_schedule = ?, last_cron_update = ?
                WHERE id IN ({})
            """.format(','.join('?' * len(article_ids))), 
            [cron_schedule, datetime.now().strftime('%Y-%m-%d %H:%M:%S')] + article_ids)
            conn.commit()
            conn.close()
            
            ui.notify(f'Successfully scheduled {len(article_ids)} articles', type='positive')
            dialog.close()
            refresh_callback()
        except Exception as e:
            ui.notify(f'Error updating schedules: {str(e)}', type='negative')
    
    return handle_bulk_cron 