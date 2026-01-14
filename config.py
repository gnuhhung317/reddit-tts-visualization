import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Reddit API Credentials
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "StoryBot/1.0")

    # Pexels API
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

    # Settings
    SUBREDDITS = ["AskReddit", "TIFU", "Confession", "TalesFromTechSupport"]
    MIN_UPVOTES = 100
    VOICE_NAME = "en-US-ChristopherNeural" # Edge-TTS voice
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
