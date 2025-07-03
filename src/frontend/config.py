import os
import logging
from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self):
        """
        Configuration loader for frontend environment variables.

        Attributes:
            HOST_NAME (str): The base hostname or domain where the backend is hosted.
            BACKEND_PORT (str): Port that the backend api is running on
        """
        self.HOST_NAME = self.get_variable("HOST_NAME")
        self.BACKEND_PORT = self.get_variable("BACKEND_PORT")
        self.VERSION = self.get_variable("VERSION")
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
