from telegram.ext import Application
from telegram import Bot
import asyncio
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = None
        self.bot = None
        logger.debug(f"TelegramBot instance created with token: {token[:5]}...")
        
    async def initialize(self):
        try:
            logger.debug("Starting bot initialization")
            self.application = (
                Application.builder()
                .token(self.token)
                .build()
            )
            logger.debug("Application built")
            
            self.bot = self.application.bot
            logger.debug("Bot instance created")
            
            # Тільки ініціалізуємо бота, але не запускаємо повний application
            await self.bot.initialize()
            logger.info("Telegram bot initialized successfully")
            return self.bot
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}", exc_info=True)
            raise

    async def shutdown(self):
        try:
            if self.bot:
                logger.debug("Starting bot shutdown")
                await self.bot.shutdown()
                logger.info("Bot instance shut down successfully")
            if self.application:
                logger.debug("Starting application shutdown")
                await self.application.shutdown()
                logger.info("Application shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)