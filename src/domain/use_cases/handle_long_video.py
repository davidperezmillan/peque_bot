from src.domain.entities.video_message import VideoMessage
from src.domain.repositories.message_repository import MessageRepository
from src.domain.repositories.video_repository import VideoRepository
from src.config.config import Config

class HandleLongVideoUseCase:
    def __init__(self, message_repository: MessageRepository, video_repository: VideoRepository, videos_dir: str):
        self.message_repository = message_repository
        self.video_repository = video_repository
        self.videos_dir = videos_dir
        self.logger = Config.get_logger('domain.use_cases.handle_long_video')

    async def execute(self, video_message: VideoMessage) -> None:
        self.logger.debug(f"Executing long video use case for message {video_message.message_id}")

        if video_message.is_long_video:
            self.logger.info(f"Downloading long video message {video_message.message_id} "
                           f"from chat {video_message.chat_id} to directory {self.videos_dir}")
            try:
                file_path = await self.video_repository.download_video(video_message, self.videos_dir)
                self.logger.info(f"Long video message {video_message.message_id} downloaded successfully to {file_path}")

                # Send confirmation message
                confirmation_text = f"✅ Video largo descargado exitosamente:\n📁 {file_path}"
                await self.message_repository.send_message(video_message.chat_id, confirmation_text)
                self.logger.info(f"Confirmation message sent for long video {video_message.message_id}")

            except Exception as e:
                self.logger.error(f"Failed to process long video message {video_message.message_id}: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.warning(f"Message {video_message.message_id} is not a long video "
                              f"(duration: {video_message.video_duration}s)")