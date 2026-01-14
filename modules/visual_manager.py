import requests
import random
import os
import re
from collections import Counter
from config import Config
from typing import List, Optional

class VisualManager:
    def __init__(self):
        self.api_key = Config.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/videos/search"
        self.fallback_dir = os.path.join("assets", "backgrounds")
        
        # Ensure fallback dir exists
        os.makedirs(self.fallback_dir, exist_ok=True)

    def extract_keywords(self, text: str, max_keywords: int = 3) -> str:
        """
        Extracts search keywords from text.
        Simple logic: remove stopwords, sort by length/frequency.
        """
        if not text:
            return "satisfying" # Generic fallback

        # Basic stopwords list
        stopwords = set(['the', 'and', 'to', 'of', 'a', 'in', 'is', 'that', 'with', 'for', 'it', 'on', 'was', 'my', 'me', 'at', 'this', 'but', 'have', 'had', 'not', 'be', 'are', 'we', 'from', 'so', 'just', 'like', 'about', 'what', 'an', 'if', 'or', 'when', 'one', 'all', 'do', 'they', 'can', 'up', 'out', 'there', 'who', 'get', 'go', 'would'])
        
        words = re.findall(r'\w+', text.lower())
        meaningful_words = [w for w in words if w not in stopwords and len(w) > 3]
        
        if not meaningful_words:
            return "satisfying"

        # Most common meaningful words might set the "theme"
        # But for Reddit stories, often "minecraft parkour" or "subway surfers" is the requested style.
        # If the user wants specific background styles, we can enforce that.
        # For "Dynamic Backgrounds" based on story:
        counts = Counter(meaningful_words)
        common = counts.most_common(max_keywords)
        
        return " ".join([w[0] for w in common])

    def search_pexels(self, query: str) -> Optional[str]:
        """
        Searches Pexels for vertical videos.
        Returns the download URL of a video.
        """
        if not self.api_key:
            print("Pexels API Key not found.")
            return None

        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "orientation": "portrait", # Vertical video
            "per_page": 5,
            "size": "medium" # Don't need 4k
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = data.get("videos", [])
            if not videos:
                return None
            
            # Pick a random video from the top 5
            video = random.choice(videos)
            
            # Get the video file url (prefer HD)
            video_files = video.get("video_files", [])
            # Sort by width/quality to match roughly 1080w if possible, or just huge
            # Simple header: look for one that is closest to portrait HD
            target_file = None
            for vf in video_files:
                if vf.get("width", 0) >= 720: # At least 720p width
                    target_file = vf
                    break
            
            if not target_file and video_files:
                target_file = video_files[0]
                
            return target_file.get("link")

        except Exception as e:
            print(f"Error searching Pexels: {e}")
            return None

    def download_video(self, url: str, output_path: str) -> bool:
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False

    def get_background_video(self, text: str = "") -> str:
        """
        Main method to get a background video path.
        Returns absolute path to video file.
        """
        keywords = self.extract_keywords(text)
        print(f"Extracted background keywords: {keywords}")
        
        # Try Pexels
        # Can force "minecraft parkour" search if generic keywords
        search_query = keywords + " aesthetic" 
        
        video_url = self.search_pexels(search_query)
        if video_url:
            output_path = os.path.join("assets", "temp", "background.mp4")
            if self.download_video(video_url, output_path):
                return output_path
        
        # Fallback to local
        print("Using fallback background.")
        # Check if any mp4 exists in fallback_dir
        files = [f for f in os.listdir(self.fallback_dir) if f.endswith(".mp4")]
        if files:
            return os.path.join(self.fallback_dir, random.choice(files))
        
        print(f"No background found in {self.fallback_dir}.")
        return ""
