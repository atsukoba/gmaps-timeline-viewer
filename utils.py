import json
import logging
import os
from datetime import datetime
from typing import Dict, Literal, Optional, TypedDict

# types


class Environment(TypedDict):
    APP_SERVER_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: Optional[str]
    DATABASE_SOCKET: Optional[str]
    DATABASE_PORT: int


with open(os.path.join(os.path.dirname(__file__), "env.json"), "r") as f:
    env: Environment = json.load(f)

loggers_dict: Dict[str, logging.Logger] = {}


def create_logger(name: str) -> logging.Logger:
    global loggers_dict
    if name in loggers_dict.keys():
        return loggers_dict[name]
    else:
        logger = logging.getLogger(name)
        loggers_dict[name] = logger
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
        d = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        fh = logging.FileHandler(os.path.join(
            os.path.dirname(__file__), "logs", d + ".log"))
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        return logger


if __name__ == "__main__":
    pass
