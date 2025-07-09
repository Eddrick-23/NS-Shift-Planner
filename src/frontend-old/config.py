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
        self.ENVIRONMENT = self.get_variable("ENVIRONMENT")
        self.check_valid_environment(self.ENVIRONMENT)
        if self.ENVIRONMENT == "DEV":
            self.BACKEND_URL = f"http://{self.get_variable("HOST_NAME")}:{self.get_variable("BACKEND_PORT")}"
        if self.ENVIRONMENT == "PROD":
            self.BACKEND_URL = f"{self.get_variable("BACKEND_DOMAIN")}"
        self.PORT = int(self.get_variable("FRONTEND_PORT"))
        self.VERSION = self.get_variable("VERSION")
        self.API_KEY = self.get_variable("API_KEY")
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
