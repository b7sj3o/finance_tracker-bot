import logging, asyncio, sys, handlers
from config import dp, bot


@dp.startup()
async def on_startup(dispatcher):
    """
    Called on bot startup. Initializes necessary components and logs the startup.
    """
    logging.info("Bot has started")


@dp.shutdown()
async def on_shutdown(dispatcher):
    """
    Called on bot shutdown. Cleans up resources and logs the shutdown.
    """
    logging.info("Bot has stopped")


async def main():
    """
    Main entry point for the bot. Starts polling for updates.
    """
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
