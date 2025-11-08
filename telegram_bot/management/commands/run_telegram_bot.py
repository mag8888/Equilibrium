import logging

from django.core.management.base import BaseCommand, CommandError
from telegram.error import InvalidToken

from telegram_bot.bot import run_polling

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram-бота Equilibrium Club в режиме long polling."

    def handle(self, *args, **options):
        try:
            run_polling()
        except InvalidToken as exc:
            raise CommandError(
                "Некорректный TELEGRAM_BOT_TOKEN. Проверьте переменную окружения."
            ) from exc
        except Exception as exc:  # pragma: no cover - runtime errors surfaced to console
            logger.exception("Ошибка при запуске Telegram-бота.")
            raise CommandError(str(exc)) from exc

