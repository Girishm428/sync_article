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
    logger.info(f"Data Base in not found, Initializing database: {DB_FILE}")
    if DB_FILE.exists():
        return # Avoid re-initializing
        
    logger.info(f"🔍 Initializing database: {DB_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            last_synced TEXT  -- Storing as TEXT for simplicity
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

# Initialize the database when this module is first imported
# init_db()