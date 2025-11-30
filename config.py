import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    @classmethod
    def validate_config(cls):
        return bool(cls.GOOGLE_API_KEY and cls.GOOGLE_API_KEY !="AIzaSyAi3vJHOQCqApdtCNvKwgjOFOqIu0RLu0I")