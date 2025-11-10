import ssl
import logging
import time
from pyVim.connect import SmartConnect, Disconnect
from dotenv import load_dotenv
import os
import atexit
from pathlib import Path

# Setup logger
logger = logging.getLogger(__name__)


def load_env():
    """
    Загрузка конфигов из перменных окружений
    """
    config_path = os.path.join(Path(__file__).parent.parent, "config", ".env")
    if not os.path.isfile(config_path):
        logger.critical("Не удалось загрузить переменные окружения")
        raise
    load_dotenv(dotenv_path=config_path)


def connect(max_retries: int = 3, delay: int = 5):
    """
    Подключение к vCenter 
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    for attempt in range(1, max_retries + 1):
        try:
            load_env()
            logger.info(f"Попытка подключения {attempt}/{max_retries} к vCenter")
            si = SmartConnect(
                host=os.getenv("VCSA_HOST"),
                user=os.getenv("VCSA_USER"),
                pwd=os.getenv("VCSA_PASS"),
                port=int(os.getenv("VCSA_PORT", 443)),
                sslContext=context
            )
            atexit.register(Disconnect, si)
            logger.info("Подключение к vCenter успешно")
            return si
        except Exception as e:
            logger.warning(f"Попытка подключения {attempt} к vCenter не удалась: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                logger.critical("Все попытки подключения к vCenter не удались")
                raise