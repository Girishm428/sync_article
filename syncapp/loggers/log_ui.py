# syncapp/loggers/log_ui.py

from typing import Callable, Awaitable
from syncapp.loggers.log_cli import setup_logger

logger = setup_logger(__name__)

status_logs: list[str] = []
_update_ui: Callable[[], Awaitable[None]] | None = None

def register_ui_updater(updater: Callable[[], Awaitable[None]]):
    global _update_ui
    _update_ui = updater
    logger.info("✅ UI updater registered.")

def clear_logs():
    logger.info("🧹 Clearing logs...")
    status_logs.clear()
    if _update_ui:
        logger.info("🔁 Calling _update_ui from clear_logs...")
        import asyncio
        asyncio.create_task(_update_ui())
    else:
        logger.warning("⚠️ _update_ui is not set during clear_logs.")

async def log_message(message: str):
    logger.info(f"📝 Logging message: {message}")
    status_logs.append(message)
    if _update_ui:
        logger.info("🔁 Calling _update_ui from log_message...")
        await _update_ui()
    else:
        logger.warning("⚠️ _update_ui is not set during log_message.")