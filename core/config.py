from dotenv import load_dotenv
import os

load_dotenv()

TOKEN_SECRETO = os.getenv("TOKEN_SECRETO")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./webhooks.db")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"