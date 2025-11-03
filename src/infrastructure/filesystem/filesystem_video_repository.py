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
        self.logger.debug(f"Starting download of video {video_message.document.id} to directory {destination_dir}")

        try:
            # Ensure destination directory exists
            os.makedirs(destination_dir, exist_ok=True)
            self.logger.debug(f"Ensured destination directory exists: {destination_dir}")

            # Generate filename: use file_name if available, otherwise use document ID
            base_filename = video_message.file_name or f"{video_message.document.id}"
            # Ensure it has .mp4 extension if not present
            if not base_filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm')):
                base_filename += '.mp4'

            file_path = os.path.join(destination_dir, base_filename)
            self.logger.info(f"Downloading video '{base_filename}' (ID: {video_message.document.id}) to {file_path}")

            # Download the video
            await self.client.download_media(video_message.document, file_path)

            # Verify file was created and get size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                filename_display = video_message.file_name or f"ID_{video_message.document.id}.mp4"
                self.logger.info(f"Video '{filename_display}' downloaded successfully. "
                               f"File size: {file_size} bytes, Path: {file_path}")
            else:
                raise FileNotFoundError(f"Downloaded file not found at {file_path}")

            return file_path

        except Exception as e:
            filename_display = video_message.file_name or f"ID_{video_message.document.id}"
            self.logger.error(f"Failed to download video '{filename_display}' (ID: {video_message.document.id}) to {destination_dir}: {str(e)}", exc_info=True)
            raise