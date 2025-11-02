from dotenv import load_dotenv
import os
import logging
import sys
from pathlib import Path

load_dotenv()

class Config:
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    VIDEO_INPUT_GROUP_ID = os.getenv('VIDEO_INPUT_GROUP_ID')
    DESTINATION_CHAT_ID = os.getenv('DESTINATION_CHAT_ID')

    # Video size limits in MB (converted to bytes internally)
    SHORT_VIDEO_MAX_BYTES = int(os.getenv('SHORT_VIDEO_MAX_MB', '50')) * (1024 * 1024)
    MEDIUM_VIDEO_MAX_BYTES = int(os.getenv('MEDIUM_VIDEO_MAX_MB', '500')) * (1024 * 1024)

    @staticmethod
    def check_video_group_ids(video_group_id: str) -> int:
        try:
            video_group_id = int(video_group_id)
            return video_group_id
        except (TypeError, ValueError):
            return None


    @staticmethod
    def rebuild_environment_variables():
        Config.VIDEO_INPUT_GROUP_ID = Config.check_video_group_ids(Config.VIDEO_INPUT_GROUP_ID)
        Config.DESTINATION_CHAT_ID = Config.check_video_group_ids(Config.DESTINATION_CHAT_ID)


    @staticmethod
    def log_chat_configuration(logger: logging.Logger) -> None:
        """Log the configured chat IDs for monitoring and debugging"""
        logger.info("=== Chat Configuration ===")
        logger.info(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
        logger.info(f"Video Input Group ID: {Config.VIDEO_INPUT_GROUP_ID}")
        logger.info(f"Destination Chat ID: {Config.DESTINATION_CHAT_ID}")
        logger.info(f"Bot Token: {'*' * len(Config.BOT_TOKEN) if Config.BOT_TOKEN else 'Not Set'}")
        logger.info("=== Video Size Limits ===")
        logger.info(f"Short Video Max: {Config.SHORT_VIDEO_MAX_BYTES // (1024*1024)} MB ({Config.SHORT_VIDEO_MAX_BYTES} bytes)")
        logger.info(f"Medium Video Max: {Config.MEDIUM_VIDEO_MAX_BYTES // (1024*1024)} MB ({Config.MEDIUM_VIDEO_MAX_BYTES} bytes)")
        logger.info("==========================")

    @staticmethod
    def setup_logging(level: str = None) -> logging.Logger:
        """Configure and return the main application logger"""

        # Get log level from environment variable if not provided
        if level is None:
            level = os.getenv('LOG_LEVEL', 'INFO')

        # Create logs directory if it doesn't exist
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)

        # Configure root logger
        logger = logging.getLogger('peque_bot')
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        # File handler
        file_handler = logging.FileHandler(logs_dir / 'peque_bot.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        return logging.getLogger(f'peque_bot.{name}')