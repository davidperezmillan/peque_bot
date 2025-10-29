from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.video_message import VideoMessage

class MessageRepository(ABC):
    @abstractmethod
    async def get_messages_from_group(self, group_id: int) -> List[VideoMessage]:
        pass

    @abstractmethod
    async def forward_message(self, message: VideoMessage, destination_chat_id: str) -> None:
        ## reenvio del mensaje a otro chat
        await self.client.send_message(destination_chat_id, message.caption, reply_to=message.message_id)
        pass

    @abstractmethod
    async def send_message_with_buttons(self, message: VideoMessage, destination_chat_id: str) -> None:
        pass

    @abstractmethod
    async def delete_message(self, message: VideoMessage) -> None:
        pass