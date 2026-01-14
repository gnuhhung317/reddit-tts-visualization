import re
import edge_tts
import asyncio
import json
import os
from config import Config
from typing import List, Dict, Any

class TTSEngine:
    def __init__(self, voice: str = Config.VOICE_NAME):
        self.voice = voice

    def clean_text(self, text: str) -> str:
        """
        Cleans text for better TTS experience.
        Removes edits, links, and weird formatting.
        """
        if not text:
            return ""
            
        # Remove markdown URLs: [text](link) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove raw URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove "Edit:" sections typical in Reddit
        text = re.sub(r'(?i)\n+edit:.*', '', text)
        
        # Remove extensive underscores or dashes
        text = re.sub(r'[_\-]{2,}', ' ', text)
        
        return text.strip()

    async def generate_audio(self, text: str, output_path: str) -> List[Dict[str, Any]]:
        """
        Generates audio file and returns word-level timestamps.
        """
        text = self.clean_text(text)
        if not text:
            return []

        communicate = edge_tts.Communicate(text, self.voice)
        
        # We need to capture the subtitle data (word boundaries)
        # edge-tts returns events.
        
        word_timings = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # chunk is dict: {'type': 'WordBoundary', 'offset': 0, 'duration': 0, 'text': 'Hello'}
                    # Convert to seconds? 
                    # offset and duration are usually in 100ns units (ticks), need to verify for edge-tts
                    # edge-tts doc: "offset": int (100ns units), "duration": int (100ns units)
                    # 1s = 10,000,000 ticks
                    
                    start_s = chunk["offset"] / 10_000_000
                    end_s = (chunk["offset"] + chunk["duration"]) / 10_000_000
                    
                    word_timings.append({
                        "word": chunk["text"],
                        "start": start_s,
                        "end": end_s
                    })

        return word_timings

    def save_subtitles_to_json(self, timings: List[Dict[str, Any]], output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(timings, f, ensure_ascii=False, indent=2)
