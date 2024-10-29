import asyncio
import logging
from app import create_app
from bot_config import TelegramBot
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from dotenv import load_dotenv
import os
import sys
from asyncio import Event

# Налаштування розширеного логування
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.debug("Starting application initialization")
        
        # Create and configure the Flask app
        app = create_app()
        logger.info("Flask app created successfully")
        
        # Initialize the Telegram bot
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
            
        logger.debug("Initializing Telegram bot")
        bot_handler = TelegramBot(bot_token)
        app.bot = await bot_handler.initialize()
        logger.info("Telegram bot initialized successfully")
        
        # Configure Hypercorn
        config = HyperConfig()
        config.bind = ["127.0.0.1:5000"]
        config.use_reloader = True
        logger.debug("Hypercorn configured")
        
        # Create shutdown event
        shutdown_event = Event()
        
        # Define shutdown handler
        async def shutdown():
            logger.debug("Starting shutdown procedure")
            try:
                await bot_handler.shutdown()
                logger.info("Bot shutdown completed")
            except Exception as e:
                logger.error(f"Error during bot shutdown: {e}")
            finally:
                shutdown_event.set()
                logger.info("Application shutdown complete")
        
        # Create proper shutdown trigger
        def shutdown_trigger():
            return shutdown_event.wait()
        
        logger.info("Starting server...")
        await serve(app, config, shutdown_trigger=shutdown_trigger)
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        logger.info("Starting main application loop")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped manually")
    except Exception as e:
        logger.error(f"Server encountered an error: {e}", exc_info=True)
        raise