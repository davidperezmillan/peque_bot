import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeVideo
from src.config.config import Config
from src.domain.entities.video_message import VideoMessage
from src.infrastructure.telegram.telegram_message_repository import TelegramMessageRepository
from src.infrastructure.filesystem.filesystem_video_repository import FilesystemVideoRepository
from src.domain.use_cases.handle_short_video import HandleShortVideoUseCase
from src.domain.use_cases.handle_medium_video import HandleMediumVideoUseCase
from src.domain.use_cases.handle_long_video import HandleLongVideoUseCase
from src.application.services.video_message_handler import VideoMessageHandlerService
from src.application.services.command_handler import CommandHandler, TelegramMessageSender

# Setup logging
logger = Config.setup_logging()
logger.info("Starting Peque Bot application")

# Initialize configuration
Config.rebuild_environment_variables()

# Log chat configuration
Config.log_chat_configuration(logger)

async def main():
    logger.info("Initializing Peque Bot...")

    # Helper function to safely convert chat ID to int
    def safe_chat_id(chat_id_str):
        ## check if chat_id_str is int or none or empty
        if chat_id_str is None:
            return None
        if isinstance(chat_id_str, int):
            return chat_id_str
        if chat_id_str and chat_id_str.strip():
            try:
                return int(chat_id_str)
            except ValueError:
                logger.warning(f"Invalid chat ID format: {chat_id_str}")
                return None
        return None

    # Initialize Telegram client
    logger.debug("Initializing Telegram client")
    client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
    await client.start(bot_token=Config.BOT_TOKEN)
    logger.info("Telegram client initialized and connected successfully")

    # Initialize repositories
    logger.debug("Initializing repositories")
    message_repo = TelegramMessageRepository(client)
    video_repo = FilesystemVideoRepository(client)
    logger.info("Repositories initialized")

    # Initialize use cases
    logger.debug("Initializing use cases")
    handle_short = HandleShortVideoUseCase(message_repo, Config.DESTINATION_CHAT_ID)
    handle_medium = HandleMediumVideoUseCase(message_repo, Config.DESTINATION_CHAT_ID)
    handle_long = HandleLongVideoUseCase(message_repo, video_repo)
    logger.info("Use cases initialized")

    # Initialize application service
    logger.debug("Initializing application services")
    handler_service = VideoMessageHandlerService(handle_short, handle_medium, handle_long)

    # Initialize command handler
    message_sender = TelegramMessageSender(client)
    command_handler = CommandHandler(message_sender)
    logger.info("Application services initialized")

    logger.info("Setting up event handlers...")

    # Convert input group ID to integer
    input_group_id = safe_chat_id(Config.VIDEO_INPUT_GROUP_ID)
    if not input_group_id:
        logger.error("VIDEO_INPUT_GROUP_ID is not configured or invalid!")
        raise ValueError("VIDEO_INPUT_GROUP_ID must be configured")

    logger.info(f"Video input group configured: {input_group_id}")

    @client.on(events.NewMessage(chats=[input_group_id]))
    async def handle_video_input_group(event):
        """Unified handler for all video messages from the input group.
        Automatically classifies videos by size and routes to appropriate use case."""
        message = event.message
        logger.info(f"Received message in video input group {input_group_id}")

        if message.video:
            video_attr = next((attr for attr in message.document.attributes if hasattr(attr, 'duration')), None)
            if video_attr:
                logger.debug(f"Processing video: size={message.document.size} bytes")

                # Extraer el nombre del archivo del documento
                file_name_attr = next((attr for attr in message.document.attributes if isinstance(attr, DocumentAttributeFilename)), None)
                file_name = file_name_attr.file_name if file_name_attr else None


                # Create video message entity
                video_message = VideoMessage(
                    message_id=message.id,
                    chat_id=message.chat_id,
                    video_duration=video_attr.duration,
                    video_size=message.document.size,
                    document=message.document,
                    caption=message.text,
                    file_name=file_name # ← NUEVO: Extraer el nombre del archivo
                )

                # Classify and route video based on size
                if video_message.is_short_video:
                    logger.info(f"Classified as SHORT video (<50MB): routing to short video handler")
                    await handler_service.handle_video_message(video_message)
                elif video_message.is_medium_video:
                    logger.info(f"Classified as MEDIUM video (50-500MB): routing to medium video handler")
                    await handler_service.handle_video_message(video_message)
                elif video_message.is_long_video:
                    logger.info(f"Classified as LONG video (>500MB): routing to long video handler")
                    await handler_service.handle_video_message(video_message)
                else:
                    logger.warning(f"Video size {message.document.size} bytes doesn't match any category")
            else:
                logger.warning(f"Video message {message.id} without duration attribute")
        else:
            logger.debug(f"Non-video message {message.id} in input group (ignored)")
    
    @client.on(events.NewMessage)
    async def handle_message(event):
        message = event.message
        logger.debug(f"Received message from chat {message.chat_id}, sender {message.sender_id}")

        # Handle commands
        if message.text and message.text.startswith('/'):
            command = message.text.split()[0].lower()
            logger.info(f"Processing command '{command}' from user {message.sender_id} in chat {message.chat_id}")

            if command == '/start':
                await command_handler.handle_start_command(message)
            elif command == '/help':
                await command_handler.handle_help_command(message)
            elif command == '/status':
                await command_handler.handle_status_command(message)
            elif command == '/stats':
                await command_handler.handle_stats_command(message)
            else:
                await command_handler.handle_unknown_command(message)
            return
    
    @client.on(events.CallbackQuery)
    async def handle_callback(event):
        data = event.data.decode('utf-8')
        logger.info(f"Received callback query: '{data}' from user {event.sender_id}")

        if data == 'send':
            logger.info(f"User {event.sender_id} approved video sending")
            await event.answer('Video enviado!')
            # enviar el video al chat de destino sin caption
            msg = await event.get_message()
            await client.send_message(Config.DESTINATION_CHAT_ID, file=msg.document)
            ## borrar el mensaje original
            await client.delete_messages(event.chat_id, msg.id)
            await event.answer('Video enviado al chat de destino!')

        elif data == 'delete':
            logger.info(f"User {event.sender_id} requested video deletion")
            msg = await event.get_message()
            await client.delete_messages(event.chat_id, msg.id)
            await event.answer('Video borrado!')
            
        elif data == 'trim_10s':
            logger.info(f"User {event.sender_id} requested video trimming to 10 seconds")
            await event.answer('Procesando video... ⏳')
            
            try:
                msg = await event.get_message()
                
                # Create VideoMessage entity from the message
                video_attr = next((attr for attr in msg.document.attributes if isinstance(attr, DocumentAttributeVideo)), None)
                if video_attr:
                    video_message = VideoMessage(
                        message_id=msg.id,
                        chat_id=msg.chat_id,
                        video_duration=video_attr.duration,
                        video_size=msg.document.size,
                        document=msg.document,
                        caption=msg.text
                    )
                    
                    lanochequepasamos = "-1002834323493"

                    # Trim and send the video to the ORIGINAL chat (where the video is)
                    # await message_repo.trim_and_send_video(video_message, [video_message.chat_id, int(lanochequepasamos)], 10)
                    await message_repo.trim_and_send_video(video_message, [int(lanochequepasamos)], 10)

                    # Delete the original message with buttons
                    # await client.delete_messages(event.chat_id, msg.id)
                    await event.answer('✅ Video recortado enviado!')
                else:
                    await event.answer('❌ Error: No se pudo procesar el video')
                    logger.error("No video attributes found in document")
                    
            except Exception as e:
                logger.error(f"Error trimming video: {str(e)}", exc_info=True)
                await event.answer('❌ Error al procesar el video')
        else:
            logger.warning(f"Unknown callback data '{data}' from user {event.sender_id}")
            await event.answer('❌ Acción no reconocida')

    logger.info("All event handlers configured. Bot is ready to receive messages.")
    logger.info("Starting message polling...")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())