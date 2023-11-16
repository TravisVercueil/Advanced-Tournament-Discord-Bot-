import os
from dotenv import load_dotenv


load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
HOST = os.getenv("host")
PASSWORD = os.getenv("password")
USER = os.getenv("user")