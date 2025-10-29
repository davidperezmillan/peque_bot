import os
from telethon import TelegramClient
from src.domain.entities.video_message import VideoMessage
from src.domain.repositories.video_repository import VideoRepository
from src.config.config import Config

class FilesystemVideoRepository(VideoRepository):
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = Config.get_logger('infrastructure.filesystem_video_repository')

    async def download_video(self, video_message: VideoMessage, destination_dir: str) -> str:
        self.logger.debug(f"Starting download of video {video_message.file_id} to directory {destination_dir}")

        try:
            # Ensure destination directory exists
            os.makedirs(destination_dir, exist_ok=True)
            self.logger.debug(f"Ensured destination directory exists: {destination_dir}")

            file_path = os.path.join(destination_dir, f"{video_message.file_id}.mp4")
            self.logger.info(f"Downloading video {video_message.file_id} to {file_path}")

            # Download the video
            await self.client.download_media(video_message.file_id, file_path)

            # Verify file was created and get size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.logger.info(f"Video {video_message.file_id} downloaded successfully. "
                               f"File size: {file_size} bytes, Path: {file_path}")
            else:
                raise FileNotFoundError(f"Downloaded file not found at {file_path}")

            return file_path

        except Exception as e:
            self.logger.error(f"Failed to download video {video_message.file_id} to {destination_dir}: {str(e)}", exc_info=True)
            raise