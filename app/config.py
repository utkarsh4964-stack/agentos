import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
APP_NAME = os.getenv("APP_NAME", "AgentOS")
DEBUG = os.getenv("DEBUG", "True") == "True"
MAX_BUDGET = float(os.getenv("MAX_BUDGET", "1.0"))
