# Arquitectura y Clases del Proyecto Peque Bot

## Estructura General del Proyecto

```
peque_bot/
├── src/
│   ├── main.py                    # Punto de entrada principal
│   ├── config/
│   │   └── config.py             # Configuración y logging
│   ├── domain/
│   │   ├── entities/
│   │   │   └── video_message.py  # Entidad VideoMessage
│   │   ├── repositories/
│   │   │   ├── message_repository.py    # Interfaz MessageRepository
│   │   │   └── video_repository.py      # Interfaz VideoRepository
│   │   └── use_cases/
│   │       ├── handle_short_video.py   # Caso de uso videos cortos
│   │       ├── handle_medium_video.py  # Caso de uso videos medios
│   │       └── handle_long_video.py    # Caso de uso videos largos
│   ├── application/
│   │   └── services/
│   │       ├── video_message_handler.py # Servicio principal de manejo de videos
│   │       └── command_handler.py       # Servicio de comandos del bot
│   └── infrastructure/
│       ├── telegram/
│       │   └── telegram_message_repository.py  # Implementación Telegram
│       └── filesystem/
│           └── filesystem_video_repository.py   # Implementación sistema de archivos
├── tests/                         # Tests unitarios
├── videos/                        # Directorio para videos descargados
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Configuración Docker
├── docker-compose.yml           # Configuración Docker Compose
└── .env.example                 # Variables de entorno de ejemplo
```

## Descripción Detallada de Clases y Archivos

### 1. main.py - Punto de Entrada Principal

**Ubicación**: `src/main.py`
**Propósito**: Inicialización y configuración del bot, registro de manejadores de eventos.

**Funciones principales**:
- `main()`: Función asíncrona principal que:
  - Configura logging
  - Valida variables de entorno
  - Inicializa repositorios, casos de uso y servicios
  - Registra manejadores de eventos
  - Inicia el polling de mensajes

**Manejadores registrados**:
- `handle_video_input_group()`: Procesa videos del grupo de entrada
- `handle_message()`: Procesa comandos del bot
- `handle_callback()`: Procesa callbacks de botones interactivos

**Funciones auxiliares**:
- `safe_chat_id()`: Convierte strings de chat ID a enteros de forma segura

---

### 2. Configuración (config/config.py)

**Ubicación**: `src/config/config.py`
**Propósito**: Gestión centralizada de configuración y logging.

**Clase Config**:
- **Atributos de clase**: Variables de entorno (API_ID, API_HASH, BOT_TOKEN, etc.)
- **Métodos estáticos**:
  - `setup_logging()`: Configura el sistema de logging con archivo y consola
  - `check_video_group_ids()`: Valida y convierte IDs de chat a enteros
  - `rebuild_environment_variables()`: Procesa variables de entorno al inicio
  - `log_chat_configuration()`: Registra configuración actual
  - `get_logger()`: Obtiene logger para módulos específicos

---

### 3. Capa de Dominio

#### 3.1 Entidad VideoMessage (domain/entities/video_message.py)

**Propósito**: Representa un mensaje de video con sus metadatos.

**Atributos**:
- `message_id`: ID único del mensaje (int)
- `chat_id`: ID del chat donde se recibió (int)
- `video_duration`: Duración en segundos (int)
- `video_size`: Tamaño en bytes (int)
- `file_id`: ID del archivo en Telegram (str)
- `caption`: Texto del mensaje (Optional[str])

**Propiedades calculadas**:
- `is_short_video`: True si duración < 20 segundos
- `is_medium_video`: True si 20 ≤ duración < 1000 segundos
- `is_long_video`: True si duración ≥ 1000 segundos

#### 3.2 Interfaces de Repositorios

**MessageRepository** (`domain/repositories/message_repository.py`):
- `send_message(chat_id, text, file_id=None)`: Envía mensaje de texto o reenvía archivo
- `send_video_with_buttons(chat_id, video_message, buttons)`: Envía video con botones interactivos

**VideoRepository** (`domain/repositories/video_repository.py`):
- `download_video(file_id, filename)`: Descarga video del sistema de archivos

#### 3.3 Casos de Uso

**HandleShortVideoUseCase** (`domain/use_cases/handle_short_video.py`):
- **Propósito**: Procesa videos cortos (< 20s)
- **Lógica**: Reenvía automáticamente al chat de destino
- **Dependencias**: MessageRepository

**HandleMediumVideoUseCase** (`domain/use_cases/handle_medium_video.py`):
- **Propósito**: Procesa videos medios (20-1000s)
- **Lógica**: Envía al destino con botones de aprobación
- **Dependencias**: MessageRepository

**HandleLongVideoUseCase** (`domain/use_cases/handle_long_video.py`):
- **Propósito**: Procesa videos largos (≥ 1000s)
- **Lógica**: Descarga al sistema de archivos
- **Dependencias**: MessageRepository, VideoRepository

---

### 4. Capa de Aplicación

#### 4.1 VideoMessageHandlerService (application/services/video_message_handler.py)

**Propósito**: Servicio principal que coordina el procesamiento de videos.

**Métodos**:
- `__init__()`: Inicializa con casos de uso para cada tipo de video
- `handle_video_message()`: Clasifica y enruta videos según duración

**Lógica de enrutamiento**:
```python
if video_message.is_short_video:
    await handle_short_video_use_case.execute(video_message)
elif video_message.is_medium_video:
    await handle_medium_video_use_case.execute(video_message)
elif video_message.is_long_video:
    await handle_long_video_use_case.execute(video_message)
```

#### 4.2 CommandHandler (application/services/command_handler.py)

**Propósito**: Maneja comandos del bot (/start, /help, etc.).

**Métodos**:
- `handle_start_command()`: Mensaje de bienvenida
- `handle_help_command()`: Información de ayuda
- `handle_status_command()`: Estado del bot
- `handle_stats_command()`: Estadísticas de uso
- `handle_unknown_command()`: Comando no reconocido

---

### 5. Capa de Infraestructura

#### 5.1 TelegramMessageRepository (infrastructure/telegram/telegram_message_repository.py)

**Propósito**: Adaptador para la API de Telegram.

**Implementa**: MessageRepository

**Métodos principales**:
- `send_message()`: Envía mensajes de texto o reenvía archivos
- `send_video_with_buttons()`: Envía videos con botones inline

**Dependencias**: TelegramClient de Telethon

#### 5.2 FilesystemVideoRepository (infrastructure/filesystem/filesystem_video_repository.py)

**Propósito**: Adaptador para operaciones del sistema de archivos.

**Implementa**: VideoRepository

**Métodos principales**:
- `download_video()`: Descarga y guarda videos localmente

**Dependencias**: TelegramClient para descarga, pathlib para rutas

#### 5.3 TelegramMessageSender (application/services/command_handler.py)

**Propósito**: Clase auxiliar para envío de mensajes en respuestas a comandos.

**Métodos**:
- `send_message()`: Envía mensaje de texto
- `send_reply()`: Responde a un mensaje específico

---

## Flujo de Datos Típico

### Procesamiento de Video Corto:
1. `main.py` recibe mensaje en `VIDEO_INPUT_GROUP_ID`
2. Extrae metadatos del video
3. Crea `VideoMessage` entity
4. `VideoMessageHandlerService` detecta `is_short_video = True`
5. Llama `HandleShortVideoUseCase.execute()`
6. `TelegramMessageRepository.send_message()` reenvía a `DESTINATION_CHAT_ID`

### Procesamiento de Video Medio:
1. `main.py` recibe mensaje en `VIDEO_INPUT_GROUP_ID`
2. Extrae metadatos del video
3. Crea `VideoMessage` entity
4. `VideoMessageHandlerService` detecta `is_medium_video = True`
5. Llama `HandleMediumVideoUseCase.execute()`
6. `TelegramMessageRepository.send_video_with_buttons()` envía con botones
7. Espera callback del usuario
8. Procesa decisión (enviar/borrar)

### Procesamiento de Video Largo:
1. `main.py` recibe mensaje en `VIDEO_INPUT_GROUP_ID`
2. Extrae metadatos del video
3. Crea `VideoMessage` entity
4. `VideoMessageHandlerService` detecta `is_long_video = True`
5. Llama `HandleLongVideoUseCase.execute()`
6. `FilesystemVideoRepository.download_video()` guarda en `VIDEOS_DIR`

## Principios de Diseño Aplicados

### Arquitectura Hexagonal
- **Separación de capas**: Dominio independiente de infraestructura
- **Inyección de dependencias**: Repositorios inyectados en casos de uso
- **Interfaces claras**: Contratos bien definidos entre capas

### SOLID Principles
- **Single Responsibility**: Cada clase tiene una responsabilidad única
- **Open/Closed**: Fácil agregar nuevos tipos de video sin modificar código existente
- **Dependency Inversion**: Dependencias de interfaces, no implementaciones

### Manejo de Errores
- Logging comprehensivo en todas las capas
- Validación de entrada en límites de capa
- Degradación elegante ante errores de configuración
- Propagación controlada de excepciones

## Escalabilidad

El diseño permite fácilmente:
- Agregar nuevos tipos de video (ej: videos muy largos, GIFs, etc.)
- Cambiar destinos de envío por tipo de video
- Modificar lógica de clasificación
- Integrar nuevos canales de notificación
- Añadir métricas y monitoreo