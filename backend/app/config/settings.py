from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


settings = Settings()