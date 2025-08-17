# import praw
# import csv
# import time
# from datetime import datetime
# from tqdm import tqdm
# import os
# from dotenv import load_dotenv
# import sys

# load_dotenv()

# def setup_reddit_api() -> praw.Reddit:
#     """Set up Reddit API connection using PRAW"""
#     client_id = os.getenv('REDDIT_CLIENT_ID') or input("Enter Reddit Client ID: ")
#     client_secret = os.getenv('REDDIT_CLIENT_SECRET') or input("Enter Reddit Client Secret: ")
#     user_agent = os.getenv('REDDIT_USER_AGENT') or input("Enter User Agent (e.g., 'ReviewScraper/1.0'): ")
#     username = os.getenv('REDDIT_USERNAME') or input("Enter Reddit Username: ")
#     password = os.getenv('REDDIT_PASSWORD') or input("Enter Reddit Password: ")

#     if not all([client_id, client_secret, user_agent]):
#         print("Error: Missing Reddit API credentials")
#         sys.exit(1)

#     try:
#         reddit = praw.Reddit(
#             client_id=client_id,
#             client_secret=client_secret,
#             user_agent=user_agent,
#             username=username,
#             password=password
#         )
#         reddit.user.me()  # test connection
#         print("✅ Reddit API connection successful")
#         return reddit
#     except Exception as e:
#         print(f"Error connecting to Reddit API: {e}")
#         sys.exit(1)


# # Aspect keyword dictionary (synonyms)
# ASPECT_KEYWORDS = {
#     "battery life": ["battery", "charging", "power", "drain"],
#     "camera quality": ["camera", "photo", "video", "shot", "selfie"],
#     "display": ["screen", "display", "oled", "lcd", "refresh rate"],
#     "performance": ["lag", "speed", "performance", "processor", "chip"],
#     "sound": ["audio", "sound", "speaker", "mic", "headphone"],
#     "build quality": ["build", "durable", "fragile", "design", "material"],
#     "connectivity": ["wifi", "5g", "network", "signal", "bluetooth"]
# }


# def extract_comments_from_post(submission, model, aspect):
#     """Extract comments from a single Reddit post, with aspect relevance flag"""
#     comments_data = []

#     try:
#         submission.comments.replace_more(limit=None)
#         all_comments = submission.comments.list()

#         # Take top 100 comments
#         top_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:100]

#         for comment in top_comments:
#             if not hasattr(comment, "body") or comment.body in ["[deleted]", "[removed]", ""]:
#                 continue

#             if len(comment.body.strip()) < 15:
#                 continue

#             # Check if aspect is mentioned via keywords
#             aspect_relevant = any(
#                 k in comment.body.lower()
#                 for k in ASPECT_KEYWORDS.get(aspect, [])
#             )

#             phone_category = f"{model} {aspect.title()}"

#             comment_data = {
#                 'review_id': comment.id,
#                 'phone_category': phone_category,
#                 'product_id': submission.id,
#                 'review_text': comment.body.replace('\n', ' ').replace('\r', ' ').strip(),
#                 'rating': None,
#                 'review_date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
#                 'helpful_votes': comment.score,
#                 'total_votes': None,
#                 'reviewer_name': str(comment.author) if comment.author else 'Anonymous',
#                 'emojis': None,
#                 'aspect_relevant': aspect_relevant
#             }
#             comments_data.append(comment_data)

#     except Exception as e:
#         print(f"⚠️ Error processing post {submission.id}: {e}")

#     return comments_data


# def search_and_extract_aspect_reviews(reddit, phone_models, aspects, max_posts_per_query=20, save_file="phone_aspect_reviews.csv"):
#     """Search for posts and extract relevant comments, saving every 500 reviews with resume support"""
#     all_reviews = []
#     saved_count = 0
#     seen_ids = set()

#     # If CSV exists, load previous reviews to resume
#     fieldnames = [
#         'review_id', 'phone_category', 'product_id', 'review_text',
#         'rating', 'review_date', 'helpful_votes', 'total_votes',
#         'reviewer_name', 'emojis', 'aspect_relevant'
#     ]

#     if os.path.exists(save_file):
#         print(f"🔄 Resuming from existing file: {save_file}")
#         with open(save_file, 'r', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 seen_ids.add(row['review_id'])
#         saved_count = len(seen_ids)
#         print(f"↪ Found {saved_count} reviews already saved")
#     else:
#         with open(save_file, 'w', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()

#     # Start scraping
#     for model in phone_models:
#         for aspect in aspects:
#             query = f"{model} {aspect}"
#             try:
#                 subreddit = reddit.subreddit("all")
#                 search_results = list(subreddit.search(
#                     query,
#                     sort="relevance",
#                     time_filter="year",
#                     limit=max_posts_per_query
#                 ))

#                 qualifying_posts = []
#                 for post in search_results:
#                     try:
#                         if post.score >= 10 and post.num_comments >= 5:
#                             qualifying_posts.append(post)
#                     except:
#                         continue

#                 for post in tqdm(qualifying_posts, desc=f"Processing {query} posts"):
#                     post_reviews = extract_comments_from_post(post, model, aspect)

#                     # Filter out already-seen reviews
#                     new_reviews = [r for r in post_reviews if r['review_id'] not in seen_ids]

#                     if new_reviews:
#                         all_reviews.extend(new_reviews)
#                         for r in new_reviews:
#                             seen_ids.add(r['review_id'])

#                     # Save every 500 reviews
#                     if len(all_reviews) >= 500:
#                         with open(save_file, 'a', newline='', encoding='utf-8') as csvfile:
#                             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                             writer.writerows(all_reviews)
#                         saved_count += len(all_reviews)
#                         all_reviews = []  # reset buffer
#                         print(f"💾 Saved {saved_count} total reviews so far")

#                     time.sleep(2)

#             except Exception as e:
#                 print(f"⚠️ Error searching for '{query}': {e}")
#                 continue

#     # Final save of leftovers
#     if all_reviews:
#         with open(save_file, 'a', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerows(all_reviews)
#         saved_count += len(all_reviews)

#     print(f"\n✅ Finished. Total reviews collected: {saved_count}")
#     return saved_count


# def main():
#     print("🚀 Starting Reddit Phone Aspect Reviews Scraper...")
#     reddit = setup_reddit_api()

#     phone_models = [
#         "iPhone 15", "iPhone 15 Pro", "iPhone 15 Pro Max",
#         "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
#         "Samsung Galaxy S24", "Samsung Galaxy S24 Ultra",
#         "Samsung Galaxy Z Fold5", "Samsung Galaxy Z Flip5",
#         "Samsung Galaxy S23", "Samsung Galaxy S23 Ultra",
#         "Google Pixel 8", "Google Pixel 8 Pro",
#         "Google Pixel 7", "Google Pixel 7 Pro",
#         "Google Pixel Fold", "Google Pixel 7a",
#         "OnePlus 12", "OnePlus 12R", "OnePlus Open",
#         "OnePlus 11", "OnePlus 10 Pro", "OnePlus Nord 3",
#         "Xiaomi 14", "Xiaomi 14 Ultra",
#         "Xiaomi 13", "Xiaomi 13 Ultra",
#         "Xiaomi Mix Fold 3", "Xiaomi Redmi Note 13 Pro+",
#         "Oppo Find X7 Ultra", "Oppo Find X6 Pro",
#         "Oppo Find N3 Flip", "Oppo Reno 10 Pro+",
#         "Oppo A98", "Oppo F25 Pro",
#         "Vivo X100 Pro", "Vivo X100",
#         "Vivo X90 Pro+"
#     ]

#     aspects = [
#         "battery life", "camera quality", "display",
#         "performance", "sound", "build quality", "connectivity"
#     ]

#     search_and_extract_aspect_reviews(reddit, phone_models, aspects, max_posts_per_query=20)


# if __name__ == "__main__":
#     main()




import praw
import csv
import time
from datetime import datetime
from tqdm import tqdm
import os
import json
from dotenv import load_dotenv
import sys

load_dotenv()

def setup_reddit_api() -> praw.Reddit:
    """Set up Reddit API connection using PRAW"""
    client_id = os.getenv('REDDIT_CLIENT_ID') or input("Enter Reddit Client ID: ")
    client_secret = os.getenv('REDDIT_CLIENT_SECRET') or input("Enter Reddit Client Secret: ")
    user_agent = os.getenv('REDDIT_USER_AGENT') or input("Enter User Agent (e.g., 'ReviewScraper/1.0'): ")
    username = os.getenv('REDDIT_USERNAME') or input("Enter Reddit Username: ")
    password = os.getenv('REDDIT_PASSWORD') or input("Enter Reddit Password: ")

    if not all([client_id, client_secret, user_agent]):
        print("Error: Missing Reddit API credentials")
        sys.exit(1)

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
        reddit.user.me()  # test connection
        print("✅ Reddit API connection successful")
        return reddit
    except Exception as e:
        print(f"Error connecting to Reddit API: {e}")
        sys.exit(1)


# Aspect keyword dictionary (synonyms)
ASPECT_KEYWORDS = {
    "battery life": ["battery", "charging", "power", "drain"],
    "camera quality": ["camera", "photo", "video", "shot", "selfie"],
    "display": ["screen", "display", "oled", "lcd", "refresh rate"],
    "performance": ["lag", "speed", "performance", "processor", "chip"],
    "sound": ["audio", "sound", "speaker", "mic", "headphone"],
    "build quality": ["build", "durable", "fragile", "design", "material"],
    "connectivity": ["wifi", "5g", "network", "signal", "bluetooth"]
}


class CheckpointManager:
    """Manages checkpoint state for resume functionality"""
    
    def __init__(self, checkpoint_file="scraper_checkpoint.json"):
        self.checkpoint_file = checkpoint_file
        self.checkpoint_data = self._load_checkpoint()
    
    def _load_checkpoint(self):
        """Load existing checkpoint data"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    print(f"🔄 Loading checkpoint from {self.checkpoint_file}")
                    print(f"📍 Last completed: {data.get('last_phone', 'None')} - {data.get('last_aspect', 'None')}")
                    return data
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️ Error loading checkpoint: {e}. Starting fresh.")
                return {"completed_combinations": [], "last_phone": None, "last_aspect": None}
        return {"completed_combinations": [], "last_phone": None, "last_aspect": None}
    
    def save_checkpoint(self, phone, aspect):
        """Save current progress to checkpoint file"""
        combination_key = f"{phone}::{aspect}"
        if combination_key not in self.checkpoint_data["completed_combinations"]:
            self.checkpoint_data["completed_combinations"].append(combination_key)
        
        self.checkpoint_data["last_phone"] = phone
        self.checkpoint_data["last_aspect"] = aspect
        self.checkpoint_data["timestamp"] = datetime.now().isoformat()
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.checkpoint_data, f, indent=2)
            print(f"💾 Checkpoint saved: {phone} - {aspect}")
        except Exception as e:
            print(f"⚠️ Error saving checkpoint: {e}")
    
    def is_combination_completed(self, phone, aspect):
        """Check if a phone+aspect combination has been completed"""
        combination_key = f"{phone}::{aspect}"
        return combination_key in self.checkpoint_data["completed_combinations"]
    
    def get_resume_position(self, phone_models, aspects):
        """Get the position to resume from"""
        last_phone = self.checkpoint_data.get("last_phone")
        last_aspect = self.checkpoint_data.get("last_aspect")
        
        if not last_phone or not last_aspect:
            return 0, 0  # Start from beginning
        
        try:
            phone_idx = phone_models.index(last_phone)
            aspect_idx = aspects.index(last_aspect)
            
            # Start from the next aspect, or next phone if we completed all aspects
            aspect_idx += 1
            if aspect_idx >= len(aspects):
                phone_idx += 1
                aspect_idx = 0
            
            return phone_idx, aspect_idx
        except ValueError:
            print("⚠️ Last processed phone/aspect not found in current lists. Starting from beginning.")
            return 0, 0
    
    def get_progress_stats(self, total_combinations):
        """Get progress statistics"""
        completed = len(self.checkpoint_data["completed_combinations"])
        return completed, total_combinations, (completed / total_combinations * 100) if total_combinations > 0 else 0


def extract_comments_from_post(submission, model, aspect):
    """Extract comments from a single Reddit post, with aspect relevance flag"""
    comments_data = []

    try:
        submission.comments.replace_more(limit=None)
        all_comments = submission.comments.list()

        # Take top 100 comments
        top_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:100]

        for comment in top_comments:
            if not hasattr(comment, "body") or comment.body in ["[deleted]", "[removed]", ""]:
                continue

            if len(comment.body.strip()) < 15:
                continue

            # Check if aspect is mentioned via keywords
            aspect_relevant = any(
                k in comment.body.lower()
                for k in ASPECT_KEYWORDS.get(aspect, [])
            )

            phone_category = f"{model} {aspect.title()}"

            comment_data = {
                'review_id': comment.id,
                'phone_category': phone_category,
                'product_id': submission.id,
                'review_text': comment.body.replace('\n', ' ').replace('\r', ' ').strip(),
                'rating': None,
                'review_date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                'helpful_votes': comment.score,
                'total_votes': None,
                'reviewer_name': str(comment.author) if comment.author else 'Anonymous',
                'emojis': None,
                'aspect_relevant': aspect_relevant
            }
            comments_data.append(comment_data)

    except Exception as e:
        print(f"⚠️ Error processing post {submission.id}: {e}")

    return comments_data


def search_and_extract_aspect_reviews(reddit, phone_models, aspects, max_posts_per_query=20, save_file="phone_aspect_reviews_817.csv"):
    """Search for posts and extract relevant comments, with checkpointing support"""
    all_reviews = []
    saved_count = 0
    seen_ids = set()
    
    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager()
    
    # Calculate total combinations for progress tracking
    total_combinations = len(phone_models) * len(aspects)
    completed_combinations, _, progress_percent = checkpoint_manager.get_progress_stats(total_combinations)
    
    print(f"📊 Progress: {completed_combinations}/{total_combinations} combinations completed ({progress_percent:.1f}%)")

    # Setup CSV file
    fieldnames = [
        'review_id', 'phone_category', 'product_id', 'review_text',
        'rating', 'review_date', 'helpful_votes', 'total_votes',
        'reviewer_name', 'emojis', 'aspect_relevant'
    ]

    if os.path.exists(save_file):
        print(f"🔄 Resuming from existing file: {save_file}")
        with open(save_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                seen_ids.add(row['review_id'])
        saved_count = len(seen_ids)
        print(f"↪ Found {saved_count} reviews already saved")
    else:
        with open(save_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # Get resume position
    start_phone_idx, start_aspect_idx = checkpoint_manager.get_resume_position(phone_models, aspects)
    
    if start_phone_idx > 0 or start_aspect_idx > 0:
        print(f"🎯 Resuming from phone index {start_phone_idx}, aspect index {start_aspect_idx}")

    # Start scraping from resume position
    for phone_idx in range(start_phone_idx, len(phone_models)):
        model = phone_models[phone_idx]
        
        # For the first phone, start from the resume aspect index, otherwise start from 0
        aspect_start_idx = start_aspect_idx if phone_idx == start_phone_idx else 0
        
        for aspect_idx in range(aspect_start_idx, len(aspects)):
            aspect = aspects[aspect_idx]
            
            # Skip if this combination was already completed
            if checkpoint_manager.is_combination_completed(model, aspect):
                print(f"⏭️  Skipping completed combination: {model} - {aspect}")
                continue
            
            query = f"{model} {aspect}"
            print(f"\n🔍 Processing: {model} - {aspect} ({phone_idx + 1}/{len(phone_models)}, {aspect_idx + 1}/{len(aspects)})")
            
            try:
                subreddit = reddit.subreddit("all")
                search_results = list(subreddit.search(
                    query,
                    sort="relevance",
                    time_filter="year",
                    limit=max_posts_per_query
                ))

                qualifying_posts = []
                for post in search_results:
                    try:
                        if post.score >= 10 and post.num_comments >= 5:
                            qualifying_posts.append(post)
                    except:
                        continue

                print(f"🎯 Found {len(qualifying_posts)} qualifying posts for '{query}'")

                for post in tqdm(qualifying_posts, desc=f"Processing {query} posts"):
                    post_reviews = extract_comments_from_post(post, model, aspect)

                    # Filter out already-seen reviews
                    new_reviews = [r for r in post_reviews if r['review_id'] not in seen_ids]

                    if new_reviews:
                        all_reviews.extend(new_reviews)
                        for r in new_reviews:
                            seen_ids.add(r['review_id'])

                    # Save every 500 reviews
                    if len(all_reviews) >= 500:
                        with open(save_file, 'a', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writerows(all_reviews)
                        saved_count += len(all_reviews)
                        all_reviews = []  # reset buffer
                        print(f"💾 Saved {saved_count} total reviews so far")

                    time.sleep(2)

                # Mark this combination as completed
                checkpoint_manager.save_checkpoint(model, aspect)
                
                # Update progress
                completed_combinations += 1
                progress_percent = (completed_combinations / total_combinations) * 100
                print(f"✅ Completed: {model} - {aspect} | Progress: {completed_combinations}/{total_combinations} ({progress_percent:.1f}%)")

            except Exception as e:
                print(f"⚠️ Error searching for '{query}': {e}")
                print("💾 Saving progress before continuing...")
                
                # Save any remaining reviews before continuing
                if all_reviews:
                    with open(save_file, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerows(all_reviews)
                    saved_count += len(all_reviews)
                    all_reviews = []
                
                continue

    # Final save of any remaining reviews
    if all_reviews:
        with open(save_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(all_reviews)
        saved_count += len(all_reviews)

    print(f"\n🎉 All combinations completed! Total reviews collected: {saved_count}")
    
    # Clean up checkpoint file when completely done
    if os.path.exists(checkpoint_manager.checkpoint_file):
        os.remove(checkpoint_manager.checkpoint_file)
        print(f"🗑️  Checkpoint file removed (scraping completed)")
    
    return saved_count


def main():
    print("🚀 Starting Reddit Phone Aspect Reviews Scraper with Checkpointing...")
    reddit = setup_reddit_api()

    phone_models = [
        "iPhone 15", "iPhone 15 Pro", "iPhone 15 Pro Max",
        "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
        "Samsung Galaxy S24", "Samsung Galaxy S24 Ultra",
        "Samsung Galaxy Z Fold5", "Samsung Galaxy Z Flip5",
        "Samsung Galaxy S23", "Samsung Galaxy S23 Ultra",
        "Google Pixel 8", "Google Pixel 8 Pro",
        "Google Pixel 7", "Google Pixel 7 Pro",
        "Google Pixel Fold", "Google Pixel 7a",
        "OnePlus 12", "OnePlus 12R", "OnePlus Open",
        "OnePlus 11", "OnePlus 10 Pro", "OnePlus Nord 3",
        "Xiaomi 14", "Xiaomi 14 Ultra",
        "Xiaomi 13", "Xiaomi 13 Ultra",
        "Xiaomi Mix Fold 3", "Xiaomi Redmi Note 13 Pro+",
        "Oppo Find X7 Ultra", "Oppo Find X6 Pro",
        "Oppo Find N3 Flip", "Oppo Reno 10 Pro+",
        "Oppo A98", "Oppo F25 Pro",
        "Vivo X100 Pro", "Vivo X100",
        "Vivo X90 Pro+"
    ]

    aspects = [
        "battery life", "camera quality", "display",
        "performance", "sound", "build quality", "connectivity"
    ]

    try:
        search_and_extract_aspect_reviews(reddit, phone_models, aspects, max_posts_per_query=20)
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user. Progress has been saved.")
        print("🔄 Run the script again to resume from where you left off.")
    except Exception as e:
        print(f"\n💥 Unexpected error occurred: {e}")
        print("🔄 Progress has been saved. Run the script again to resume.")


if __name__ == "__main__":
    main()