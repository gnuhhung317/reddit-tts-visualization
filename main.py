import asyncio
from config import Config

async def main():
    print("Starting Reddit Story Automation Pipeline...")
    
    # Step 1: Data Acquisition
    print("Step 1: Fetching stories from Reddit...")
    from modules.reddit_scraper import RedditScraper
    scraper = RedditScraper()
    stories = scraper.fetch_stories(limit=1)
    
    if not stories:
        print("No stories found matching criteria.")
        return

    selected_story = stories[0]
    print(f"Selected Story: {selected_story['title']} (r/{selected_story['subreddit']})")

    # Capture Screenshot
    print("Capturing screenshot...")
    from modules.screenshot_manager import ScreenshotManager
    # Note: Screenshotting can be slow, might want to run in parallel or cache
    ss_manager = ScreenshotManager()
    screenshot_path = ss_manager.capture_post_title(selected_story['url'], selected_story['id'])
    ss_manager.close()
    
    if screenshot_path:
        print(f"Screenshot saved to: {screenshot_path}")
    else:
        print("Failed to capture screenshot.")


    
    # Step 2: TTS
    print("Step 2: Converting text to speech...")
    from modules.tts_engine import TTSEngine
    import os
    
    tts = TTSEngine()
    
    # Process Title
    title_audio_path = os.path.join("assets", "temp", "title.mp3")
    title_timings_path = os.path.join("assets", "temp", "title_timings.json")
    print("Generating Title Audio...")
    title_timings = await tts.generate_audio(selected_story['title'], title_audio_path)
    tts.save_subtitles_to_json(title_timings, title_timings_path)
    
    # Process Content (First paragraph only for testing if long)
    content_text = selected_story['content']
    if len(content_text) > 500:
        content_text = content_text[:500] + "..." # Truncate for testing
    
    content_audio_path = os.path.join("assets", "temp", "content.mp3")
    content_timings_path = os.path.join("assets", "temp", "content_timings.json")
    print("Generating Content Audio...")
    content_timings = await tts.generate_audio(content_text, content_audio_path)
    tts.save_subtitles_to_json(content_timings, content_timings_path)
    
    print(f"Audio generated at {title_audio_path} and {content_audio_path}")
    
    # Step 3: Backgrounds
    print("Step 3: Fetching background visuals...")
    from modules.visual_manager import VisualManager
    vm = VisualManager()
    
    # Use content text to find relevant bg
    background_video_path = vm.get_background_video(selected_story['content'])
    
    if background_video_path:
        print(f"Background video ready: {background_video_path}")
    else:
        print("No background video found (check assets/backgrounds/ or Pexels key).")
        # Creating a dummy file so pipeline doesn't crash in next steps if we want to proceed?
        # Or just return
        if not os.path.exists(os.path.join("assets", "backgrounds")):
             print("Please add a video to 'assets/backgrounds/' for fallback.")

    
    # Step 4: Assembly
    print("Step 4: Assembling video...")
    from modules.video_editor import VideoAssembler
    
    if background_video_path and os.path.exists(background_video_path):
        assembler = VideoAssembler()
        
        output_file = os.path.join("assets", "final_video.mp4")
        
        files_map = {
            'title_audio': title_audio_path,
            'title_timings': title_timings,
            'title_screenshot': screenshot_path if screenshot_path else None,
            'content_audio': content_audio_path,
            'content_timings': content_timings
        }
        
        assembler.assemble_video(background_video_path, files_map, output_file)
        print(f"Pipeline finished! Check {output_file}")
    else:
        print("Skipping assembly (missing background).")
    
    print("Pipeline completed!")

if __name__ == "__main__":
    asyncio.run(main())
