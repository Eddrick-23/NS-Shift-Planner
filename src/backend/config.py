import os
import logging
from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self):
        """
        Configuration loader for backend environment variables.

        Attributes:
            HOST_NAME (str): The base hostname or domain where the backend is hosted.
            GOOGLE_APPLICATION_CREDENTIALS (str): Path to the Google Cloud service account JSON credentials file.
            LRU_CACHE_SIZE (int): Maximum number of items allowed in the in-memory LRU cache.
            PRUNE_DB_INTERVAL (int): Time interval (in hours) for periodically pruning expired data from the database.
            DATA_EXPIRY_LENGTH (int): Duration (in days) after which session data is considered expired and will be delete during DB Pruning.
            SCAN_CACHE_INTERVAL (int): Time interval (in minutes) for scanning and refreshing the in-memory cache.
        """

        self.ENVIRONMENT = self.get_variable("ENVIRONMENT")
        self.check_valid_environment(self.ENVIRONMENT)
        if self.ENVIRONMENT == "PROD":
            self.FRONT_END_DOMAIN = self.get_variable("FRONT_END_DOMAIN")
        else:
            self.FRONT_END_DOMAIN = None
        self.GOOGLE_APPLICATION_CREDENTIALS = self.get_variable(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.DB_COLLECTION_NAME = self.get_variable("DB_COLLECTION_NAME")
        self.API_KEY = self.get_variable("API_KEY")
        self.LRU_CACHE_SIZE = int(self.get_variable("LRU_CACHE_SIZE"))
        self.PRUNE_DB_INTERVAL = int(self.get_variable("PRUNE_DB_INTERVAL"))
        self.DATA_EXPIRY_LENGTH = int(self.get_variable("DATA_EXPIRY_LENGTH"))
        self.SCAN_CACHE_INTERVAL = int(self.get_variable("SCAN_CACHE_INTERVAL"))
        logging.info("Backend configs loaded")
    
    def check_valid_environment(self,environement:str):
        if environement not in ["DEV","PROD"]:
            raise RuntimeError("Invalid ENVIRONMENT env variable should be DEV/PROD")

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
