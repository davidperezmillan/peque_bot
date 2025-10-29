from src.domain.entities.video_message import VideoMessage
from src.domain.repositories.message_repository import MessageRepository
from src.config.config import Config

class HandleShortVideoUseCase:
    def __init__(self, message_repository: MessageRepository, destination_chat_id: str):
        self.message_repository = message_repository
        self.destination_chat_id = destination_chat_id
        self.logger = Config.get_logger('domain.use_cases.handle_short_video')

    async def execute(self, video_message: VideoMessage) -> None:
        self.logger.debug(f"Executing short video use case for message {video_message.message_id}")

        if video_message.is_short_video:
            self.logger.info(f"Forwarding short video message {video_message.message_id} "
                           f"from chat {video_message.chat_id} to destination {self.destination_chat_id}")
            try:
                await self.message_repository.forward_message(video_message, self.destination_chat_id)
                self.logger.info(f"Short video message {video_message.message_id} forwarded successfully")
            except Exception as e:
                self.logger.error(f"Failed to forward short video message {video_message.message_id}: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.warning(f"Message {video_message.message_id} is not a short video "
                              f"(duration: {video_message.video_duration}s)")