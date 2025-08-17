# main.py

import os
import sys
import praw
from dotenv import load_dotenv

# --- IMPORTANT ---
# Load environment variables AT THE VERY TOP, before any other project imports.
load_dotenv()

# Now, import the other modules from your project
from scraper import search_and_extract
from utils import save_to_csv
from gemini_analyzer import setup_gemini # Import the new setup function

def setup_reddit_api() -> praw.Reddit:
    """Set up and validate Reddit API connection."""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    
    if not all([client_id, client_secret, user_agent, username, password]):
        print("❌ Error: Missing one or more Reddit API credentials in .env file.")
        sys.exit(1)
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
        reddit.user.me()
        print("✅ Reddit API connection successful.")
        return reddit
    except Exception as e:
        print(f"❌ Error connecting to Reddit API: {e}")
        sys.exit(1)

def main():
    """Main function to run the phone review scraper."""
    print("🚀 Starting Reddit Phone Review Scraper...")

    # --- EXPLICIT API KEY SETUP ---
    # 1. Load the Google API Key from the environment
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    # 2. Add a print statement to confirm if the key is loaded
    if google_api_key:
        print("🔑 Google API Key loaded from .env file.")
    else:
        print("🚨 CRITICAL ERROR: Could not load GOOGLE_API_KEY from .env file.")
        print("   Please ensure your .env file is in the same directory and has the correct key.")
        sys.exit(1)

    # 3. Setup the APIs
    setup_gemini(google_api_key) # <-- Explicitly configure Gemini
    reddit = setup_reddit_api()
    # --- END OF SETUP ---
    
    phone_queries = [
        "iPhone 15 Pro review", "iPhone 15 Pro battery life", "iPhone 15 camera",
        "Samsung Galaxy S24 Ultra review", "Galaxy S24 camera test",
        "Google Pixel 8 Pro review", "Pixel 8 after 6 months",
        "OnePlus 12 review", "OnePlus Open durability",
        "Xiaomi 14 Ultra camera review",
        "Nothing Phone (2) review"
    ]
    
    print(f"📱 Searching for reviews across {len(phone_queries)} queries...")
    reviews = search_and_extract(reddit, phone_queries, max_posts_per_query=10)
    
    if reviews:
        unique_reviews = list({review['review_id']: review for review in reviews}.values())
        print(f"\n📊 Extracted {len(unique_reviews)} unique and valid reviews.")
        save_to_csv(unique_reviews)
    else:
        print("\n❌ No reviews could be extracted. Try broader search terms or check API credentials.")

if __name__ == "__main__":
    main()