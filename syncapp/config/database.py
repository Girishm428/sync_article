import sqlite3
from pathlib import Path
from syncapp.loggers.log_cli import setup_logger
from platformdirs import user_config_dir

#------------ logger ------------
logger = setup_logger(__name__)

#------------ Database ------------
APP_NAME = "SyncImporter"
CONFIG_DIR = Path(user_config_dir(APP_NAME, appauthor=False))  # appauthor=False prevents duplicate folder
DB_FILE = CONFIG_DIR / "articles.db"
logger.info(f"🔍 Database file: {DB_FILE}")


def get_db_connection():
    """Establishes a connection to the database."""
    logger.info(f"🔍 Establishing connection to database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    logger.info(f"🔍 Initializing database: {DB_FILE}")
    if DB_FILE.exists():
        # Check if we need to add new columns
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get list of existing columns
        cursor.execute("PRAGMA table_info(articles)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'cron_schedule' not in existing_columns:
            logger.info("Adding cron_schedule column")
            cursor.execute("ALTER TABLE articles ADD COLUMN cron_schedule TEXT")
        
        if 'last_cron_update' not in existing_columns:
            logger.info("Adding last_cron_update column")
            cursor.execute("ALTER TABLE articles ADD COLUMN last_cron_update TEXT")
            
        conn.commit()
        conn.close()
        return
        
    logger.info(f"🔍 Creating new database: {DB_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_url TEXT NOT NULL,
            article_id TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            last_synced TEXT,
            cron_schedule TEXT,
            last_cron_update TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")