from enum import StrEnum


class Config(StrEnum):
    TELEGRAM_URL = 'https://api.telegram.org/bot'
    TELEGRAM_MESSAGE_LIMIT = str(4096)
    TELEGRAM_CAPTION_LIMIT = str(1024)
    TELEGRAM_REQUEST_TIMEOUT = str(60)

    CHAT_TYPE_GROUP = 'group'
    CHAT_TYPE_CHANNEL = 'channel'
    CHAT_TYPE_SUPER_GROUP = 'supergroup'

    SUCCESS = 'success'
    ERROR = 'error'
    INFORMATION = 'information'