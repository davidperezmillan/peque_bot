from src.domain.entities.video_message import VideoMessage
from src.domain.repositories.message_repository import MessageRepository
from src.config.config import Config

class HandleMediumVideoUseCase:
    def __init__(self, message_repository: MessageRepository, destination_chat_id: str):
        self.message_repository = message_repository
        self.destination_chat_id = destination_chat_id
        self.logger = Config.get_logger('domain.use_cases.handle_medium_video')

    async def execute(self, video_message: VideoMessage) -> None:
        self.logger.debug(f"Executing medium video use case for message {video_message.message_id}")

        if video_message.is_medium_video:
            self.logger.info(f"Sending medium video message {video_message.message_id} "
                           f"from chat {video_message.chat_id} to origin chat {video_message.chat_id} with approval buttons")
            try:
                await self.message_repository.send_message_with_buttons(video_message, video_message.chat_id, "⚠️ Este video es de tamaño medio. ¿Deseas enviarlo al chat de destino?")
                self.logger.info(f"Medium video message {video_message.message_id} sent with buttons successfully")
                # borrar el mensaje original
                await self.message_repository.delete_message(video_message)
            except Exception as e:
                self.logger.error(f"Failed to send medium video message {video_message.message_id} with buttons: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.warning(f"Message {video_message.message_id} is not a medium video "
                              f"(duration: {video_message.video_duration}s)")