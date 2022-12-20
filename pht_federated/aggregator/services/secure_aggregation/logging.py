from loguru import logger


def protocol_warning(protocol_id: str, message: str):
    logger.warning(f"Protocol - {protocol_id} - {message}")


def protocol_info(protocol_id: str, message: str):
    logger.info(f"Protocol - {protocol_id} - {message}")


def protocol_error(protocol_id: str, message: str):
    logger.error(f"Protocol - {protocol_id} - {message}")


def protocol_debug(protocol_id: str, message: str):
    logger.debug(f"Protocol - {protocol_id} - {message}")
