from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


@dataclass
class TelegramConfig:
    token: str
    web_app_url: str


def build_application(config: Optional[TelegramConfig] = None) -> Application:
    config = config or TelegramConfig(
        token=settings.TELEGRAM_BOT_TOKEN,
        web_app_url=settings.TELEGRAM_WEBAPP_URL,
    )
    application = Application.builder().token(config.token).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Добро пожаловать в Equilibrium!",
        )

    application.add_handler(CommandHandler("start", start))
    return application
