from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoMessage:
    message_id: int
    chat_id: int
    video_duration: int  # in seconds
    video_size: int  # in bytes
    file_id: str
    caption: Optional[str] = None

    @property
    def is_short_video(self) -> bool:
        """Videos cortos: menos de 20 segundos"""
        return self.video_duration < 20

    @property
    def is_medium_video(self) -> bool:
        """Videos medianos: entre 20 segundos y 1000 segundos"""
        return 20 <= self.video_duration < 1000

    @property
    def is_long_video(self) -> bool:
        """Videos largos: más de 1000 segundos"""
        return self.video_duration >= 1000