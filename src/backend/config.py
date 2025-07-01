import os
import logging
from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self):
        self.HOST_NAME = self.get_variable("HOST_NAME")
        self.GOOGLE_APPLICATION_CREDENTIALS = self.get_variable(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.LRU_CACHE_SIZE = int(self.get_variable("LRU_CACHE_SIZE"))
        logging.info("Backend configs loaded")

    def get_variable(self, key: str) -> str:
        """
        Get environment variable, raises error if it does not exist
        """
        value = os.getenv(key)
        if value is None:
            raise RuntimeError(
                f"{key} required but not found in Environment Variables."
            )

        return value


config = Config()
