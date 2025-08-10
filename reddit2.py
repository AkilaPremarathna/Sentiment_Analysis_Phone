import praw
import pandas as pd
from datetime import datetime
import re
import time
import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv


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

def extract_phone_model(text: str, subreddit_name: str) -> str:
    """Extract phone model from text or default to subreddit"""
    # Common phone model patterns
    patterns = [
        r'iPhone\s*(\d+\s*Pro\s*Max|Pro\s*Max|\d+\s*Pro|Pro|\d+)',
        r'Galaxy\s*S\d+|Note\s*\d+|Galaxy\s*A\d+',
        r'Pixel\s*\d+\s*Pro\s*XL|Pixel\s*\d+\s*XL|Pixel\s*\d+\s*Pro|Pixel\s*\d+',
        r'OnePlus\s*\d+T?|Nord\s*\d*',
        r'Xiaomi\s*\d+|Mi\s*\d+|Redmi\s*\w+',
        r'Huawei\s*P\d+|Mate\s*\d+'
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().strip()
    
    return subreddit_name.lower()

def extract_rating(text: str) -> Optional[float]:
    """Extract numerical rating from text"""
    # Pattern for ratings like "8/10", "4/5", "9 out of 10"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*/\s*10',
        r'(\d+(?:\.\d+)?)\s*/\s*5',
        r'(\d+(?:\.\d+)?)\s*out\s*of\s*10',
        r'(\d+(?:\.\d+)?)\s*out\s*of\s*5',
        r'rate\s*it\s*(\d+(?:\.\d+)?)\s*/\s*\d+',
        r'rating:\s*(\d+(?:\.\d+)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating = float(match.group(1))
            # Normalize to 0-10 scale
            if '/5' in pattern or 'out of 5' in pattern:
                rating = rating * 2
            return min(rating, 10)
    
    return None



def is_review_related(title: str, text: str) -> bool:
    """Check if post/comment is review-related"""
    keywords = [
        'review', 'experience', 'battery', 'camera', 'performance', 
        'screen', 'display', 'quality', 'opinion', 'thoughts',
        'recommend', 'worth', 'upgrade', 'pros', 'cons', 'rating', 'good' , 'bad',
        'sound' , 'user experience' 
                ]
    
    combined_text = (title + ' ' + text).lower()
    return any(keyword in combined_text for keyword in keywords)

def extract_review_data(item, item_type: str, subreddit_name: str) -> Dict:
    """Extract review data from Reddit post or comment"""
    if item_type == 'post':
        text = item.title + ' ' + (item.selftext or '')
        title = item.title
    else:  # comment
        text = item.body
        title = ''
    
    # Skip if text is too short or deleted/removed
    if len(text) < 50 or text in ['[deleted]', '[removed]']:
        return None
    
    # Check if it's review-related
    if not is_review_related(title, text):
        return None
    
    return {
        'review_id': item.id,
        'phone_category': extract_phone_model(text, subreddit_name),
        'product_id': getattr(item, 'permalink', item.id),
        'review_text': text.strip(),
        'rating': extract_rating(text),
        'review_date': datetime.fromtimestamp(item.created_utc).strftime('%Y-%m-%d'),
        'helpful_votes': item.score,
        'total_votes': max(item.score, 1),  # PRAW doesn't expose downvotes
        'reviewer_name': str(item.author) if item.author else '[deleted]'
    }

def scrape_subreddit(reddit: praw.Reddit, subreddit_name: str, limit: int = 100) -> List[Dict]:
    """Scrape posts and comments from a specific subreddit"""
    reviews = []
    seen_ids = set()
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Scraping r/{subreddit_name}...")
        
        # Scrape from hot, new, and top posts
        sections = [
            ('hot', subreddit.hot(limit=limit//3)),
            ('new', subreddit.new(limit=limit//3)),
            ('top', subreddit.top(limit=limit//3, time_filter='year'))
        ]
        
        for section_name, posts in sections:
            print(f"  Processing {section_name} posts...")
            
            for post in posts:
                # Skip if already processed
                if post.id in seen_ids:
                    continue
                seen_ids.add(post.id)
                
                # Extract post data
                post_data = extract_review_data(post, 'post', subreddit_name)
                if post_data:
                    reviews.append(post_data)
                
                # Extract top comments
                try:
                    post.comments.replace_more(limit=2)  # Load more comments
                    for comment in post.comments[:5]:  # Top 5 comments per post
                        if comment.id not in seen_ids:
                            seen_ids.add(comment.id)
                            comment_data = extract_review_data(comment, 'comment', subreddit_name)
                            if comment_data:
                                reviews.append(comment_data)
                except Exception as e:
                    print(f"    Error processing comments: {e}")
                
                # Rate limiting
                time.sleep(0.1)
                
                if len(reviews) >= limit:
                    break
            
            if len(reviews) >= limit:
                break
                
    except Exception as e:
        print(f"Error scraping r/{subreddit_name}: {e}")
    
    print(f"  Collected {len(reviews)} reviews from r/{subreddit_name}")
    return reviews

def scrape_smartphone_reviews(reddit: praw.Reddit, target_count: int = 5000) -> pd.DataFrame:
    """Main function to scrape smartphone reviews from multiple subreddits"""
    subreddits = ['iphone', 'Android', 'GooglePixel', 'samsung', 'OnePlus', 'xiaomi', 'gadgets']
    all_reviews = []
    reviews_per_subreddit = target_count // len(subreddits)
    
    print(f"Starting to scrape {target_count} smartphone reviews...")
    
    for subreddit_name in subreddits:
        subreddit_reviews = scrape_subreddit(reddit, subreddit_name, reviews_per_subreddit)
        all_reviews.extend(subreddit_reviews)
        
        print(f"Total reviews collected so far: {len(all_reviews)}")
        
        if len(all_reviews) >= target_count:
            break
        
        # Rate limiting between subreddits
        time.sleep(2)
    
    # Create DataFrame
    df = pd.DataFrame(all_reviews)
    
    if not df.empty:
        # Remove duplicates based on review_id
        df = df.drop_duplicates(subset=['review_id'])
        
        # Filter for minimum text length
        df = df[df['review_text'].str.len() >= 50]
        
    
        
        print(f"\nFinal dataset: {len(df)} unique reviews")
        print(f"Date range: {df['review_date'].min()} to {df['review_date'].max()}")
        print(f"Phone categories: {df['phone_category'].value_counts().head()}")
    
    return df

def save_data(df: pd.DataFrame, filename: str = 'reddit_smartphone_reviews.csv'):
    """Save DataFrame to CSV file"""
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nData saved to {filename}")
        
        # Display sample data
        print(f"\nSample data preview:")
        print(df[['phone_category', 'rating', 'review_date', 'helpful_votes']].head(10))
        
        # Basic statistics
        print(f"\nDataset Statistics:")
        print(f"Total reviews: {len(df)}")
        print(f"Reviews with ratings: {df['rating'].notna().sum()}")
        print(f"Average helpful votes: {df['helpful_votes'].mean():.2f}")
        print(f"Top phone categories:\n{df['phone_category'].value_counts().head()}")
        
    except Exception as e:
        print(f"Error saving data: {e}")

def main():
    """Main execution function"""
    try:
        # Setup Reddit API
        reddit = setup_reddit_api()
        
        # Scrape reviews
        df = scrape_smartphone_reviews(reddit, target_count=50000)
        
        if not df.empty:
            # Save data
            save_data(df)
        else:
            print("No reviews were collected. Please check your API credentials and internet connection.")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()