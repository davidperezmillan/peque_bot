from src.domain.entities.video_message import VideoMessage
from src.domain.use_cases.handle_short_video import HandleShortVideoUseCase
from src.domain.use_cases.handle_medium_video import HandleMediumVideoUseCase
from src.domain.use_cases.handle_long_video import HandleLongVideoUseCase
from src.config.config import Config

class VideoMessageHandlerService:
    def __init__(
        self,
        handle_short_video_use_case: HandleShortVideoUseCase,
        handle_medium_video_use_case: HandleMediumVideoUseCase,
        handle_long_video_use_case: HandleLongVideoUseCase
    ):
        self.handle_short_video_use_case = handle_short_video_use_case
        self.handle_medium_video_use_case = handle_medium_video_use_case
        self.handle_long_video_use_case = handle_long_video_use_case
        self.logger = Config.get_logger('application.video_message_handler')

    async def handle_video_message(self, video_message: VideoMessage) -> None:
        self.logger.info(f"Processing video message: ID={video_message.message_id}, "
                        f"Chat={video_message.chat_id}, "
                        f"Duration={video_message.video_duration}s, "
                        f"Size={video_message.video_size} bytes")

        try:
            if video_message.is_short_video:
                self.logger.info(f"Routing to short video handler (duration: {video_message.video_duration}s)")
                await self.handle_short_video_use_case.execute(video_message)
                self.logger.info(f"Short video processing completed for message {video_message.message_id}")

            elif video_message.is_medium_video:
                self.logger.info(f"Routing to medium video handler (duration: {video_message.video_duration}s)")
                await self.handle_medium_video_use_case.execute(video_message)
                self.logger.info(f"Medium video processing completed for message {video_message.message_id}")

            elif video_message.is_long_video:
                self.logger.info(f"Routing to long video handler (duration: {video_message.video_duration}s)")
                await self.handle_long_video_use_case.execute(video_message)
                self.logger.info(f"Long video processing completed for message {video_message.message_id}")

            else:
                self.logger.warning(f"Video duration {video_message.video_duration}s doesn't match any category for message {video_message.message_id}")

        except Exception as e:
            self.logger.error(f"Error processing video message {video_message.message_id}: {str(e)}", exc_info=True)
            raise