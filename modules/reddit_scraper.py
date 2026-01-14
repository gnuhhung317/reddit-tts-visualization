import praw
import time
from config import Config
from typing import List, Dict, Any

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )

    def fetch_stories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches top stories from configured subreddits.
        """
        stories = []
        for subreddit_name in Config.SUBREDDITS:
            print(f"Scraping r/{subreddit_name}...")
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Fetch hot posts; can be changed to top(time_filter="day")
            posts = subreddit.hot(limit=limit * 2) 

            for post in posts:
                if len(stories) >= limit:
                    break
                
                if post.stickied:
                    continue
                
                # Filtering logic
                if post.score < Config.MIN_UPVOTES:
                    continue
                
                # Check for body length (too short or too long)
                # TIFU/Confession usually have selftext
                if not post.selftext and not post.title:
                    continue
                    
                story_data = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.selftext,
                    "url": post.url,
                    "subreddit": subreddit_name,
                    "author": str(post.author),
                    "score": post.score,
                    "num_comments": post.num_comments
                }
                stories.append(story_data)
        
        return stories

    def get_post_comments(self, post_id: str, limit: int = 3) -> List[str]:
        """
        Fetches top comments for a post.
        """
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)
        comments = []
        for comment in submission.comments.list()[:limit]:
            comments.append(comment.body)
        return comments
