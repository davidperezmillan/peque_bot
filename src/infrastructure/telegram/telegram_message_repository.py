from typing import List
from telethon import TelegramClient
from telethon.tl.types import Message as TLMessage, DocumentAttributeVideo
from telethon.tl.custom import Button
import asyncio
import os
import tempfile
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
                [Button.inline('Enviar', 'send'), Button.inline('Borrar', 'delete')],
                [Button.inline('✂️ Recortar 10s', 'trim_10s')]
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

    async def trim_and_send_video(self, message: VideoMessage, destination_chat_id: str, trim_duration: int = 10) -> None:
        """Trim video to specified duration from the center and send to destination"""
        self.logger.debug(f"Trimming video {message.message_id} to {trim_duration} seconds and sending to {destination_chat_id}")
        
        temp_input_path = None
        temp_output_path = None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
                temp_input_path = temp_input.name
            with tempfile.NamedTemporaryFile(delete=False, suffix="_trimmed.mp4") as temp_output:
                temp_output_path = temp_output.name

            # Download the video
            self.logger.debug(f"Downloading video {message.message_id} to {temp_input_path}")
            await self.client.download_file(message.document, temp_input_path)
            
            # Calculate start time from center
            start_time = max(0, (message.video_duration - trim_duration) // 2)
            
            # Use ffmpeg to trim the video
            ffmpeg_cmd = [
                "ffmpeg", "-i", temp_input_path,
                "-ss", str(start_time),
                "-t", str(trim_duration),
                "-c", "copy",  # Use copy to avoid re-encoding when possible
                "-avoid_negative_ts", "make_zero",
                temp_output_path, "-y"
            ]
            
            self.logger.debug(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown ffmpeg error"
                self.logger.error(f"FFmpeg failed with return code {process.returncode}: {error_msg}")
                raise Exception(f"Video trimming failed: {error_msg}")
                
            # Send the trimmed video
            self.logger.debug(f"Sending trimmed video to {destination_chat_id}")
            caption = f"🎬 Video recortado ({trim_duration}s desde el centro)\n{message.caption or ''}"
            await self.client.send_file(destination_chat_id, temp_output_path, caption=caption)
            
            self.logger.info(f"Trimmed video sent successfully to {destination_chat_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to trim and send video {message.message_id}: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up temporary files
            for temp_path in [temp_input_path, temp_output_path]:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        self.logger.debug(f"Cleaned up temporary file: {temp_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to clean up temporary file {temp_path}: {str(e)}")