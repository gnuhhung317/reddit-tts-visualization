from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List
import time
import os

class ScreenshotManager:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        # Ensure dark mode if possible (Reddit might default to light, we can inject CSS)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def capture_screenshot(self, url: str, output_path: str, element_selector: str = None) -> bool:
        try:
            self.driver.get(url)
            time.sleep(3) # Wait for load. reliable enough for a script.

            # Inject CSS for Dark Mode / Clean look
            dark_mode_script = """
            document.documentElement.classList.add('theme-dark');
            document.body.style.background = '#1A1A1B';
            """
            self.driver.execute_script(dark_mode_script)
            time.sleep(1)

            # Accept cookies if modal exists (simple try)
            try:
                # This selector is a guess, finding by text usually works better but varies
                pass 
            except:
                pass

            if element_selector:
                element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
                element.screenshot(output_path)
            else:
                self.driver.save_screenshot(output_path)
            
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False

    def close(self):
        self.driver.quit()

    def capture_post_title(self, url: str, post_id: str) -> str:
        """
        Captures the main post title and body (if short).
        Returns the path to the screenshot.
        """
        # Reddit's structure changes, but shreddit-post is common in new UI
        # or div[data-test-id="post-content"]
        
        # We'll use a specific customized view if possible, or just the post container
        # For now, let's target the post container in the new Reddit UI
        selector = "shreddit-post" 
        
        output_file = os.path.join("assets", "temp", f"{post_id}_title.png")
        if self.capture_screenshot(url, output_file, selector):
             return output_file
        return ""

    def capture_comment(self, url: str, comment_id: str) -> str:
        # Construct permalink to comment? 
        # Or find by id on the page
        selector = f"#t1_{comment_id}" # Reddit usually uses thing_id 
        output_file = os.path.join("assets", "temp", f"{comment_id}.png")
        if self.capture_screenshot(url, output_file, selector):
            return output_file
        return ""
