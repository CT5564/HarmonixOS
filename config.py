import os
from dotenv import load_dotenv

load_dotenv()

DEV_CHANNEL = int(os.getenv("DEV_CHANNEL"))