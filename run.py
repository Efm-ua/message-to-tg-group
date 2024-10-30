# run.py
import asyncio
import logging
import sys
from app import create_app
from telegram.ext import Application
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

async def init_bot(app):
    """Initialize Telegram bot"""
    try:
        application = Application.builder().token(app.config['TELEGRAM_BOT_TOKEN']).build()
        app.bot = application.bot
        await app.bot.initialize()
        logger.info("Telegram bot initialized successfully")
        return app.bot
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        raise

async def shutdown_bot(app):
    """Shutdown Telegram bot"""
    try:
        if app and app.bot:
            await app.bot.shutdown()
            logger.info("Telegram bot shut down successfully")
    except Exception as e:
        logger.error(f"Error during bot shutdown: {e}")

async def main():
    app = None
    try:
        # Create and setup application
        app = create_app()
        await init_bot(app)
        
        # Configure and start server
        config = HyperConfig()
        config.bind = ["127.0.0.1:5000"]
        
        logger.info("Starting server...")
        await serve(app, config)
        
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        if app:
            await shutdown_bot(app)
        logger.info("Server shutdown completed")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped via Ctrl+C")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)