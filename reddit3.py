import praw
import csv
import time
import re
from datetime import datetime
from tqdm import tqdm
import os
from dotenv import load_dotenv
import sys


load_dotenv()
def setup_reddit_api() -> praw.Reddit:
    """Set up Reddit API connection using PRAW"""
    # Get credentials from environment variables or prompt user
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
        # Test connection
        reddit.user.me()
        print("Reddit API connection successful")
        return reddit
    except Exception as e:
        print(f"Error connecting to Reddit API: {e}")
        sys.exit(1)

def infer_phone_category(title, body=""):
    """Infer phone category from post title and body"""
    text = f"{title} {body}".lower()
    
    # iPhone variants
    iphone_patterns = [
        r'iphone\s*(\d+(\s*pro(\s*max)?)?)',
        r'iphone\s*(se|xr|xs|x|plus|mini)',
        r'ios\s*\d+', r'apple\s*phone'
    ]
    
    # Samsung variants
    samsung_patterns = [
        r'samsung\s*galaxy\s*(s\d+|note\d+|a\d+|z\s*(fold|flip))',
        r'galaxy\s*(s\d+|note\d+|a\d+)',
        r'samsung\s*(phone|mobile)'
    ]
    
    # Other phone brands
    other_patterns = [
        r'pixel\s*\d+', r'google\s*pixel',
        r'oneplus\s*\d+', r'huawei\s*p\d+',
        r'xiaomi', r'oppo', r'vivo',
        r'lg\s*g\d+', r'sony\s*xperia'
    ]
    
    # Check iPhone patterns
    for pattern in iphone_patterns:
        match = re.search(pattern, text)
        if match:
            return f"iPhone {match.group(1) if match.group(1) else '15'}"
    
    # Check Samsung patterns
    for pattern in samsung_patterns:
        match = re.search(pattern, text)
        if match:
            model = match.group(1) if match.group(1) else 'S24'
            return f"Samsung Galaxy {model}"
    
    # Check other brands
    for pattern in other_patterns:
        if re.search(pattern, text):
            return "Other Phone"
    
    # Default fallback
    return "iPhone 15"

def extract_comments_from_post(submission, phone_queries):
    """Extract comments from a single Reddit post"""
    comments_data = []
    
    try:
        # Replace MoreComments objects to get all comments
        submission.comments.replace_more(limit=None)
        
        # Get all comments (including nested ones)
        all_comments = submission.comments.list()
        
        # Limit to top 50 comments by score
        top_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:50]
        
        for comment in top_comments:
            # Skip deleted/removed comments
            if not hasattr(comment, 'body') or comment.body in ["[deleted]", "[removed]", ""]:
                continue
            
            # Skip comments that are too short (likely not reviews)
            if len(comment.body.strip()) < 10:
                continue
            
            # Extract comment data
            try:
                comment_data = {
                    'review_id': comment.id,
                    'phone_category': infer_phone_category(submission.title, comment.body),
                    'product_id': submission.id,  # Use post ID as product proxy
                    'review_text': comment.body.replace('\n', ' ').replace('\r', ' ').strip(),
                    'rating': None,  # To be inferred later
                    'review_date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                    'helpful_votes': comment.score,
                    'total_votes': None,  # To be computed later
                    'reviewer_name': str(comment.author) if comment.author else 'Anonymous',
                    'emojis': None  # To be extracted later
                }
                comments_data.append(comment_data)
                
            except Exception as e:
                # Skip individual comment errors
                continue
                
    except Exception as e:
        print(f"Error processing post {submission.id}: {e}")
        
    return comments_data

def search_and_extract_reviews(reddit, phone_queries, max_posts_per_query=100):
    """Search for posts and extract comments as reviews"""
    all_reviews = []
    
    for query in phone_queries:
        print(f"🔍 Searching for: {query}")
        
        try:
            # Search across all subreddits
            subreddit = reddit.subreddit('all')
            search_results = list(subreddit.search(
                query, 
                sort="relevance", 
                time_filter="year", 
                limit=max_posts_per_query
            ))
            
            print(f"Found {len(search_results)} posts for '{query}'")
            
            # Filter posts by quality criteria
            qualifying_posts = []
            for post in search_results:
                try:
                    if post.score >= 50 and post.num_comments >= 10:
                        qualifying_posts.append(post)
                except:
                    continue
            
            print(f"Qualified posts: {len(qualifying_posts)}")
            
            # Process each qualifying post
            for i, post in enumerate(tqdm(qualifying_posts, desc=f"Processing {query} posts")):
                try:
                    post_reviews = extract_comments_from_post(post, phone_queries)
                    all_reviews.extend(post_reviews)
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except praw.exceptions.PRAWException as e:
                    print(f"PRAW error on post {post.id}: {e}")
                    continue
                except Exception as e:
                    print(f"General error on post {post.id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            continue
            
        print(f"Collected {len(all_reviews)} total reviews so far")
    
    return all_reviews

def save_to_csv(reviews_data, filename="phone_reviews.csv"):
    """Save reviews data to CSV file"""
    if not reviews_data:
        print("No reviews data to save")
        return
    
    fieldnames = [
        'review_id', 'phone_category', 'product_id', 'review_text', 
        'rating', 'review_date', 'helpful_votes', 'total_votes', 
        'reviewer_name', 'emojis'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews_data)
        
        print(f"✓ Successfully saved {len(reviews_data)} reviews to {filename}")
        
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")

def main():
    """Main function to orchestrate the scraping process"""
    print("🚀 Starting Reddit Phone Reviews Scraper...")
    
   

    # Setup Reddit API
    reddit = setup_reddit_api()
    # Define search queries for different phone types
    phone_queries = [
    "iPhone 15 review",
    "iPhone 15 Pro review",
    "iPhone 15 Pro Max review",
    "Samsung Galaxy S24 review",
    "Samsung Galaxy S24 Ultra review",
    "Samsung Galaxy Z Fold5 review",
    "Samsung Galaxy Z Flip5 review",
    "Google Pixel 8 review",
    "Google Pixel 8 Pro review",
    "OnePlus 12 review",
    "OnePlus Open review",
    "Xiaomi 14 review",
    "Xiaomi 14 Ultra review",
    "Oppo Find X7 Ultra review",
    "Oppo Find N3 Flip review",
    "Vivo X100 Pro review",
    "Vivo X100 review",
    "Asus ROG Phone 8 review",
    "Nothing Phone (2) review",
    "Motorola Edge 40 Pro review"
]

    
    # Extract reviews
    print(f"📱 Searching for reviews across {len(phone_queries)} queries...")
    reviews = search_and_extract_reviews(reddit, phone_queries, max_posts_per_query=50)
    
    if reviews:
        # Remove duplicates based on review_id
        unique_reviews = []
        seen_ids = set()
        for review in reviews:
            if review['review_id'] not in seen_ids:
                unique_reviews.append(review)
                seen_ids.add(review['review_id'])
        
        print(f"📊 Extracted {len(unique_reviews)} unique reviews")
        
        # Save to CSV
        save_to_csv(unique_reviews, "phone_reviews.csv")
        
        # Print summary statistics
        print("\n📈 Summary Statistics:")
        phone_counts = {}
        for review in unique_reviews:
            category = review['phone_category']
            phone_counts[category] = phone_counts.get(category, 0) + 1
        
        for phone, count in sorted(phone_counts.items()):
            print(f"  {phone}: {count} reviews")
            
    else:
        print("❌ No reviews extracted")

if __name__ == "__main__":
    main()