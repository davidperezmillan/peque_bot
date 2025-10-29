# Peque Bot

Un bot de Telegram construido con Telethon usando arquitectura hexagonal para gestionar mensajes de video desde un solo grupo de entrada con clasificación automática.

## Características

1. **Entrada Unificada de Videos**: Todos los videos llegan a un solo grupo y son clasificados automáticamente por duración
2. **Clasificación Automática**:
   - **Videos Cortos**: < 20 segundos - Reenvío automático al chat de destino
   - **Videos Medianos**: 20-1000 segundos - Sistema interactivo de aprobación con botones enviar/borrar
   - **Videos Largos**: > 1000 segundos - Descarga al sistema de archivos para almacenamiento
3. **Arquitectura Escalables**: Fácil agregar nuevas categorías de procesamiento de video

## Arquitectura

Este proyecto sigue la arquitectura hexagonal con:
- **Dominio**: Entidades, interfaces de repositorios y casos de uso
- **Aplicación**: Servicios que coordinan casos de uso
- **Infraestructura**: Adaptadores para Telegram y sistema de archivos

## Lógica de Clasificación de Videos

```
Grupo de Entrada (VIDEO_INPUT_GROUP_ID)
    ↓
Llega video con metadatos de duración
    ↓
Clasificación:
├── Duración < 20s → Manejador de Videos Cortos
│   └── Reenvío automático a DESTINATION_CHAT_ID
├── 20s ≤ Duración < 1000s → Manejador de Videos Medios
│   ├── Mostrar botones de aprobación (Enviar/Borrar)
│   └── Requiere interacción del usuario
└── Duración ≥ 1000s → Manejador de Videos Largos
    └── Descargar a VIDEOS_DIR
```

## Configuración

1. Copia `.env.example` a `.env` y completa tus credenciales de la API de Telegram.
2. Ejecuta con Docker Compose: `docker-compose up --build`

## Documentación Adicional

Para información detallada sobre la arquitectura, clases y funcionamiento interno del proyecto, consulta:

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Documentación completa de clases, archivos y flujo de datos

## Variables de Entorno

- `API_ID`: ID de la API de Telegram
- `API_HASH`: Hash de la API de Telegram
- `BOT_TOKEN`: Token del bot
- `LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL). Por defecto: INFO
- `VIDEO_INPUT_GROUP_ID`: ID del grupo donde se reciben todos los videos y se clasifican automáticamente
- `DESTINATION_CHAT_ID`: Chat de destino para videos cortos reenviados y aprobaciones de videos medios
- `VIDEOS_DIR`: Directorio para videos largos descargados

## Flujo de la Aplicación

### 1. Fase de Inicialización
```
main.py → Config.setup_logging() → TelegramClient.start()
    ↓
Config.rebuild_environment_variables() → Validar VIDEO_INPUT_GROUP_ID
    ↓
Inicializar Repositorios (TelegramMessageRepository, FilesystemVideoRepository)
    ↓
Inicializar Casos de Uso (HandleShortVideoUseCase, HandleMediumVideoUseCase, HandleLongVideoUseCase)
    ↓
Inicializar Servicios de Aplicación (VideoMessageHandlerService, CommandHandler)
    ↓
Registrar Manejadores de Eventos → Iniciar polling
```

### 2. Flujo de Procesamiento de Videos
```
Nuevo Mensaje en VIDEO_INPUT_GROUP_ID
    ↓
¿Es mensaje de video? → No → Ignorar
    ↓
Extraer metadatos del video (duración, tamaño, file_id)
    ↓
Crear entidad VideoMessage
    ↓
Clasificar por duración:
├── < 20 segundos → Flujo de Video Corto
│   ├── HandleShortVideoUseCase.execute()
│   ├── TelegramMessageRepository.send_message()
│   └── Reenviar a DESTINATION_CHAT_ID
├── 20-1000 segundos → Flujo de Video Medio
│   ├── HandleMediumVideoUseCase.execute()
│   ├── Enviar a DESTINATION_CHAT_ID con botones de aprobación
│   ├── Esperar callback del usuario (Enviar/Borrar)
│   └── Procesar decisión del usuario
└── ≥ 1000 segundos → Flujo de Video Largo
    ├── HandleLongVideoUseCase.execute()
    ├── FilesystemVideoRepository.download_video()
    └── Guardar en VIDEOS_DIR
```

### 3. Flujo de Procesamiento de Comandos
```
Cualquier chat → Mensaje comienza con '/'
    ↓
CommandHandler enruta por comando:
├── /start → Mensaje de bienvenida
├── /help → Información de ayuda
├── /status → Estado del bot
├── /stats → Estadísticas de uso
└── Desconocido → Mensaje de error
```

### 4. Flujo de Procesamiento de Callbacks
```
Usuario hace clic en botón en mensaje de video medio
    ↓
Evento CallbackQuery con datos ('send' o 'delete')
    ↓
'send' → Reenviar video a destino
    ↓
'delete' → Borrar mensaje del chat
```

## Capas de Arquitectura

### Capa de Dominio
- **Entidades**: `VideoMessage` - Estructura de datos para información de video
- **Casos de Uso**: Lógica de negocio para procesamiento de cada tipo de video
- **Repositorios**: Interfaces para acceso a datos (contratos)

### Capa de Aplicación
- **Servicios**: Coordinan casos de uso y manejan reglas de negocio
- **VideoMessageHandlerService**: Enruta videos a casos de uso apropiados
- **CommandHandler**: Procesa comandos del bot

### Capa de Infraestructura
- **TelegramMessageRepository**: Adaptador de API de Telegram para mensajería
- **FilesystemVideoRepository**: Adaptador de sistema de archivos para almacenamiento de video
- **Config**: Gestión de configuración de entorno

## Manejo de Errores

- IDs de chat inválidos → Advertencias registradas, degradación elegante
- Metadatos de video faltantes → Advertencias registradas, mensaje ignorado
- Errores de red/API → Errores registrados, excepciones propagadas
- Errores de configuración → Fallo de inicio de aplicación con mensajes claros