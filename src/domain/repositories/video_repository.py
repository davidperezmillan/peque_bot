from abc import ABC, abstractmethod
from src.domain.entities.video_message import VideoMessage

class VideoRepository(ABC):
    @abstractmethod
    async def download_video(self, video_message: VideoMessage, destination_dir: str) -> str:
        """Download video and return the file path"""
        pass