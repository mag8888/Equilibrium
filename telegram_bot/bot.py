from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    token: str
    webapp_url: str
    support_chat: Optional[str] = None


class EquilibriumBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.application: Optional[Application] = None

    def build_application(self) -> Application:
        if not self.config.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

        application = ApplicationBuilder().token(self.config.token).build()

        application.add_handler(CommandHandler("start", self.handle_start))
        application.add_handler(CommandHandler("app", self.handle_app))
        application.add_handler(
            MessageHandler(filters.COMMAND, self.handle_unknown_command)
        )
        application.add_handler(MessageHandler(~filters.COMMAND, self.handle_text))

        self.application = application
        return application

    async def _send_app_link(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        intro_text: str,
    ) -> None:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Открыть приложение",
                        web_app=WebAppInfo(url=self.config.webapp_url),
                    )
                ]
            ]
        )
        await update.effective_chat.send_message(
            intro_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    async def handle_start(
        self, update: Update, context: CallbackContext
    ) -> None:  # pragma: no cover - bot runtime is manual
        await self._send_app_link(
            update,
            context,
            (
                "Привет! Я бот Equilibrium Club.\n"
                "Используйте команду /app или кнопку ниже, чтобы открыть мини-приложение с партнёрской структурой."
            ),
        )

    async def handle_app(
        self, update: Update, context: CallbackContext
    ) -> None:  # pragma: no cover - bot runtime is manual
        await self._send_app_link(
            update,
            context,
            "Открываем мини-приложение:",
        )

    async def handle_unknown_command(
        self, update: Update, context: CallbackContext
    ) -> None:  # pragma: no cover - bot runtime is manual
        await update.effective_chat.send_message(
            "Неизвестная команда. Попробуйте /app, чтобы открыть мини-приложение."
        )

    async def handle_text(
        self, update: Update, context: CallbackContext
    ) -> None:  # pragma: no cover - bot runtime is manual
        await self._send_app_link(
            update,
            context,
            "Чтобы открыть мини-приложение, нажмите кнопку ниже или введите /app.",
        )


def build_bot_from_settings() -> EquilibriumBot:
    config = BotConfig(
        token=settings.TELEGRAM_BOT_TOKEN,
        webapp_url=settings.TELEGRAM_WEBAPP_URL,
        support_chat=getattr(settings, "TELEGRAM_SUPPORT_CHAT", None),
    )
    return EquilibriumBot(config=config)


def run_polling() -> None:
    bot = build_bot_from_settings()
    application = bot.build_application()
    logger.info("Starting Equilibrium Telegram bot via long polling.")
    application.run_polling()

