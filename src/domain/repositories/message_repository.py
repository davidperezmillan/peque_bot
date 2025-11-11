from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.video_message import VideoMessage

class MessageRepository(ABC):
    @abstractmethod
    async def get_messages_from_group(self, group_id: int) -> List[VideoMessage]:
        pass

    @abstractmethod
    async def forward_message(self, message: VideoMessage, destination_chat_id: str) -> None:
        pass

    @abstractmethod
    async def send_message_with_buttons(self, message: VideoMessage, destination_chat_id: str, alert_text: str) -> None:
        pass

    @abstractmethod
    async def send_medium_video_with_buttons(self, message: VideoMessage, destination_chat_id: str, alert_text: str) -> None:
        pass

    @abstractmethod
    async def delete_message(self, message: VideoMessage) -> None:
        pass

    @abstractmethod
    async def edit_message_caption(self, message: VideoMessage, new_caption: str) -> None:
        pass

    @abstractmethod
    async def send_message(self, chat_id: int, text: str, file=None) -> None:
        pass

    @abstractmethod
    async def send_reply(self, chat_id: int, text: str, reply_to_message_id: int) -> None:
        pass

    @abstractmethod
    async def trim_and_send_video(self, message: VideoMessage, destination_chat_id: list[int], trim_duration: int = 10) -> None:
        pass