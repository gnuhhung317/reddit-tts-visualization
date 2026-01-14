from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, ImageClip, CompositeVideoClip, concatenate_audioclips
from moviepy.video.tools.subtitles import SubtitlesClip
import os
from typing import List, Dict, Any, Tuple
from config import Config

class VideoAssembler:
    def __init__(self, output_width=1080, output_height=1920):
        self.width = output_width
        self.height = output_height
        self.safe_margin = 100

    def create_caption_clips(self, timings: List[Dict[str, Any]], fontsize=70, color='white', stroke_color='black', stroke_width=2) -> List[TextClip]:
        """
        Creates individual TextClips for dynamic captions.
        timings: list of dicts with 'word', 'start', 'end'
        """
        clips = []
        for timing in timings:
            word = timing['word']
            start = timing['start']
            end = timing['end']
            duration = end - start
            
            # Create TextClip
            # Note: Method might vary slightly depending on MoviePy version (v1 vs v2)
            # Assuming v1 common usage
            try:
                txt_clip = TextClip(
                    word, 
                    fontsize=fontsize, 
                    color=color, 
                    font='Arial-Bold', 
                    stroke_color=stroke_color, 
                    stroke_width=stroke_width,
                    method='caption',
                    size=(self.width - 200, None) # Wrap text if needed, though usually single words
                )
                txt_clip = txt_clip.set_position('center').set_start(start).set_duration(duration)
                clips.append(txt_clip)
            except Exception as e:
                print(f"Error creating text clip for word '{word}': {e}")
                # Fallback or invalid configuration (ImageMagick missing)
                return []
        
        return clips

    def assemble_video(self, 
                       background_path: str,
                       files_map: Dict[str, Any],
                       output_path: str):
        """
        files_map: {
            'title_audio': str,
            'title_timings': List,
            'title_screenshot': str,
            'content_audio': str,
            'content_timings': List
        }
        """
        print("Assembling video...")
        
        # Load Resources
        try:
            bg_clip = VideoFileClip(background_path)
        except Exception as e:
            print(f"Failed to load background video: {e}")
            return

        title_audio = AudioFileClip(files_map['title_audio'])
        content_audio = AudioFileClip(files_map['content_audio'])
        
        # Concatenate Audio
        final_audio = concatenate_audioclips([title_audio, content_audio])
        total_duration = final_audio.duration
        
        # Prepare Background (Loop if needed)
        if bg_clip.duration < total_duration:
            bg_clip = bg_clip.loop(duration=total_duration)
        else:
            bg_clip = bg_clip.subclip(0, total_duration)
            
        bg_clip = bg_clip.resize(height=self.height)
        # Center crop
        if bg_clip.w > self.width:
            bg_clip = bg_clip.crop(x1=bg_clip.w/2 - self.width/2, width=self.width, height=self.height)
        
        # 1. Title Section
        # Overlay Screenshot for the duration of title audio
        title_duration = title_audio.duration
        
        clips_to_overlay = []
        
        if files_map.get('title_screenshot') and os.path.exists(files_map['title_screenshot']):
            title_img = ImageClip(files_map['title_screenshot']).set_duration(title_duration).set_position('center')
            # Resize if too wide
            if title_img.w > self.width - 100:
                title_img = title_img.resize(width=self.width - 100)
            
            clips_to_overlay.append(title_img)
            
        # 2. Content Section (Dynamic Captions)
        # Offset timings by title_duration
        content_timings = files_map.get('content_timings', [])
        offset_timings = []
        for t in content_timings:
            offset_timings.append({
                'word': t['word'],
                'start': t['start'] + title_duration,
                'end': t['end'] + title_duration
            })
            
        captions = self.create_caption_clips(offset_timings)
        clips_to_overlay.extend(captions)
        
        # Combine
        final_video = CompositeVideoClip([bg_clip] + clips_to_overlay)
        final_video.audio = final_audio
        
        # Write File
        print(f"Writing video to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            threads=4
        )
        print("Video generation complete!")
