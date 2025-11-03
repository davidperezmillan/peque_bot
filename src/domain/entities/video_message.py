from dataclasses import dataclass
from typing import Optional
from src.config.config import Config

@dataclass
class VideoMessage:
    message_id: int
    chat_id: int
    video_duration: int  # in seconds
    video_size: int  # in bytes
    document: any  # Telegram document object
    caption: Optional[str] = None
    file_name: Optional[str] = None  # Optional: Name of the file

    @property
    def is_short_video(self) -> bool:
        """Videos pequeños: menos del límite configurado"""
        return self.video_size < Config.SHORT_VIDEO_MAX_BYTES

    @property
    def is_medium_video(self) -> bool:
        """Videos medianos: entre los límites configurados"""
        return Config.SHORT_VIDEO_MAX_BYTES <= self.video_size < Config.MEDIUM_VIDEO_MAX_BYTES

    @property
    def is_long_video(self) -> bool:
        """Videos largos: más del límite configurado"""
        return self.video_size >= Config.MEDIUM_VIDEO_MAX_BYTES