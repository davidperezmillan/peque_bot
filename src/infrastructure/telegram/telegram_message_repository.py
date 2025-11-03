from typing import List
from telethon import TelegramClient
from telethon.tl.types import Message as TLMessage, DocumentAttributeVideo
from telethon.tl.custom import Button
from src.domain.entities.video_message import VideoMessage
from src.domain.repositories.message_repository import MessageRepository
from src.config.config import Config

class TelegramMessageRepository(MessageRepository):
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = Config.get_logger('infrastructure.telegram_message_repository')

    async def get_messages_from_group(self, group_id: int) -> List[VideoMessage]:
        self.logger.debug(f"Retrieving messages from group {group_id}")
        messages = []
        try:
            async for message in self.client.iter_messages(group_id, limit=10):  # adjust limit
                if message.video:
                    video_attr = next((attr for attr in message.document.attributes if isinstance(attr, DocumentAttributeVideo)), None)
                    if video_attr:
                        video_message = VideoMessage(
                            message_id=message.id,
                            chat_id=message.chat_id,
                            video_duration=video_attr.duration,
                            video_size=message.document.size,
                            document=message.document,
                            caption=message.text
                        )
                        messages.append(video_message)
                        self.logger.debug(f"Found video message {message.id} with duration {video_attr.duration}s")
            self.logger.info(f"Retrieved {len(messages)} video messages from group {group_id}")
        except Exception as e:
            self.logger.error(f"Error retrieving messages from group {group_id}: {str(e)}", exc_info=True)
            raise
        return messages

    async def forward_message(self, message: VideoMessage, destination_chat_id: str) -> None:
        self.logger.debug(f"Forwarding message {message.message_id} from chat {message.chat_id} to {destination_chat_id}")
        try:
            # Enviar el archivo sin caption en lugar de reenviar
            await self.client.send_message(destination_chat_id, file=message.document)
            self.logger.info(f"Message {message.message_id} sent successfully to {destination_chat_id} without caption")
        except Exception as e:
            self.logger.error(f"Failed to send message {message.message_id} to {destination_chat_id}: {str(e)}", exc_info=True)
            raise

    async def send_message_with_buttons(self, message: VideoMessage, destination_chat_id: str, alert_text: str) -> None:
        self.logger.debug(f"Sending message with buttons for video {message.message_id} to {destination_chat_id}")
        try:
            buttons = [
                [Button.inline('Enviar', 'send'), Button.inline('Borrar', 'delete')]
            ]
            await self.client.send_message(destination_chat_id, message.caption or alert_text, buttons=buttons, file=message.document)
            self.logger.info(f"Message with buttons sent successfully for video {message.message_id} to {destination_chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to send message with buttons for video {message.message_id} to {destination_chat_id}: {str(e)}", exc_info=True)
            raise

    async def delete_message(self, message: VideoMessage) -> None:
        self.logger.debug(f"Deleting message {message.message_id} from chat {message.chat_id}")
        try:
            await self.client.delete_messages(message.chat_id, message.message_id)
            self.logger.info(f"Message {message.message_id} deleted successfully from chat {message.chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete message {message.message_id} from chat {message.chat_id}: {str(e)}", exc_info=True)
            raise

    async def send_message(self, chat_id: int, text: str, file=None) -> None:
        self.logger.debug(f"Sending message to chat {chat_id}")
        try:
            await self.client.send_message(chat_id, text, file=file)
            self.logger.debug(f"Message sent successfully to chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to send message to chat {chat_id}: {str(e)}", exc_info=True)
            raise

    async def send_reply(self, chat_id: int, text: str, reply_to_message_id: int) -> None:
        self.logger.debug(f"Sending reply to message {reply_to_message_id} in chat {chat_id}")
        try:
            await self.client.send_message(chat_id, text, reply_to=reply_to_message_id)
            self.logger.debug(f"Reply sent successfully to chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to send reply to chat {chat_id}: {str(e)}", exc_info=True)
            raise

    async def edit_message_caption(self, message: VideoMessage, new_caption: str) -> None:
        self.logger.debug(f"Editing caption of message {message.message_id} in chat {message.chat_id}")
        try:
            await self.client.edit_message(message.chat_id, message.message_id, text=new_caption)
            self.logger.info(f"Caption of message {message.message_id} edited successfully")
        except Exception as e:
            self.logger.error(f"Failed to edit caption of message {message.message_id}: {str(e)}", exc_info=True)
            raise