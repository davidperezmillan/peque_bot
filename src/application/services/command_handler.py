from typing import Protocol
from telethon import TelegramClient
from telethon.tl.custom import Message
from src.config.config import Config


class MessageSender(Protocol):
    """Protocol for sending messages"""
    async def send_message(self, chat_id: int, text: str) -> None:
        ...


class TelegramMessageSender:
    """Adapter for sending messages via Telegram"""
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = Config.get_logger('infrastructure.telegram_message_sender')

    async def send_message(self, chat_id: int, text: str) -> None:
        self.logger.debug(f"Sending message to chat {chat_id}")
        await self.client.send_message(chat_id, text)
        self.logger.debug(f"Message sent successfully to chat {chat_id}")


class CommandHandler:
    """Application service for handling bot commands"""

    def __init__(self, message_sender: MessageSender):
        self.message_sender = message_sender
        self.logger = Config.get_logger('application.command_handler')

    async def handle_start_command(self, message: Message) -> None:
        """Handle /start command"""
        self.logger.info(f"Handling /start command from user {message.sender_id} in chat {message.chat_id}")
        welcome_text = (
            "🤖 ¡Hola! Soy Peque Bot\n\n"
            "Puedo ayudarte a gestionar videos de diferentes duraciones:\n"
            "• Videos cortos (< 30 segundos)\n"
            "• Videos medianos (30 segundos - 5 minutos)\n"
            "• Videos largos (> 5 minutos)\n\n"
            "Envía /help para más información."
        )
        await self.message_sender.send_message(message.chat_id, welcome_text)
        self.logger.info(f"Start command response sent to user {message.sender_id}")

    async def handle_help_command(self, message: Message) -> None:
        """Handle /help command"""
        self.logger.info(f"Handling /help command from user {message.sender_id} in chat {message.chat_id}")
        help_text = (
            "📋 **Comandos disponibles:**\n\n"
            "/start - Iniciar el bot\n"
            "/help - Mostrar esta ayuda\n"
            "/status - Ver estado del bot\n"
            "/stats - Ver estadísticas\n\n"
            "🎥 **Funcionalidades:**\n\n"
            "• **Videos cortos**: Requieren aprobación\n"
            "• **Videos medianos**: Requieren aprobación\n"
            "• **Videos largos**: Se descargan y almacenan\n\n"
            "Simplemente envía un video a los grupos correspondientes."
        )
        await self.message_sender.send_message(message.chat_id, help_text)
        self.logger.info(f"Help command response sent to user {message.sender_id}")

    async def handle_status_command(self, message: Message) -> None:
        """Handle /status command"""
        self.logger.info(f"Handling /status command from user {message.sender_id} in chat {message.chat_id}")
        status_text = (
            "✅ **Estado del Bot**\n\n"
            "• Bot: Activo\n"
            "• Conexión: OK\n"
            "• Procesamiento: Listo\n\n"
            "¡Todo funcionando correctamente!"
        )
        await self.message_sender.send_message(message.chat_id, status_text)
        self.logger.info(f"Status command response sent to user {message.sender_id}")

    async def handle_stats_command(self, message: Message) -> None:
        """Handle /stats command"""
        self.logger.info(f"Handling /stats command from user {message.sender_id} in chat {message.chat_id}")
        stats_text = (
            "📊 **Estadísticas**\n\n"
            "• Videos procesados: --\n"
            "• Videos pendientes: --\n"
            "• Espacio usado: --\n\n"
            "_Estadísticas próximamente_"
        )
        await self.message_sender.send_message(message.chat_id, stats_text)
        self.logger.info(f"Stats command response sent to user {message.sender_id}")

    async def handle_unknown_command(self, message: Message) -> None:
        """Handle unknown commands"""
        command = message.text.split()[0] if message.text else "unknown"
        self.logger.warning(f"Unknown command '{command}' from user {message.sender_id} in chat {message.chat_id}")
        unknown_text = (
            "❓ Comando no reconocido.\n\n"
            "Envía /help para ver los comandos disponibles."
        )
        await self.message_sender.send_message(message.chat_id, unknown_text)
        self.logger.info(f"Unknown command response sent to user {message.sender_id}")