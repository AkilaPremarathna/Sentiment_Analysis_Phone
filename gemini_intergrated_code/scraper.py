# scraper.py

import praw
import time
from datetime import datetime
from tqdm import tqdm
from gemini_analyzer import analyze_review_with_gemini # Import Gemini function

def extract_comments_from_post(submission):
    """Extract and analyze comments from a single Reddit post."""
    comments_data = []
    
    print(f"\nProcessing Post: '{submission.title}' ({submission.num_comments} comments)")
    
    try:
        submission.comments.replace_more(limit=None)
        all_comments = submission.comments.list()
        
        # Filter for high-quality comments
        top_comments = sorted([c for c in all_comments if hasattr(c, 'body') and len(c.body) > 50], key=lambda c: c.score, reverse=True)[:20]

        for comment in tqdm(top_comments, desc="Analyzing comments"):
            if comment.body in ["[deleted]", "[removed]", ""]:
                continue

            # Analyze the comment with Gemini
            analysis_result = analyze_review_with_gemini(submission.title, comment.body)
            
            if not analysis_result or analysis_result.get("phone_model") in ["N/A", "Unknown Phone"]:
                continue # Skip if Gemini couldn't identify the phone

            # Populate the feature set
            review_summary = analysis_result.get("review_summary", {})
            review_data = {
                'review_id': comment.id,
                'phone_category': analysis_result.get("phone_model"),
                'product_id': submission.id,
                'review_text': comment.body.replace('\n', ' ').strip(),
                'rating': analysis_result.get("rating"),
                'review_date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                'helpful_votes': comment.score,
                'total_votes': None,  # Reddit API does not provide total votes (upvotes + downvotes)
                'reviewer_name': str(comment.author) if comment.author else 'Anonymous',
                'battery_review': review_summary.get('battery', 'N/A'),
                'camera_review': review_summary.get('camera', 'N/A'),
                'screen_review': review_summary.get('screen', 'N/A'),
                'performance_review': review_summary.get('performance', 'N/A'),
                'design_build_review': review_summary.get('design_build', 'N/A'),
                'long_term_review': review_summary.get('long_term_issues', 'N/A'),
            }
            comments_data.append(review_data)
            time.sleep(1) # To respect API rate limits

    except Exception as e:
        print(f"Error processing post {submission.id}: {e}")
        
    return comments_data

def search_and_extract(reddit, phone_queries, max_posts_per_query=20):
    """Search Reddit for relevant posts and extract reviews from them."""
    all_reviews = []
    
    for query in phone_queries:
        print(f"\n🔍 Searching for query: '{query}'")
        try:
            subreddit = reddit.subreddit('all')
            # Filter for posts with significant discussion
            search_results = [
                post for post in subreddit.search(query, sort="relevance", time_filter="year", limit=max_posts_per_query)
                if post.score >= 20 and post.num_comments >= 15
            ]
            
            print(f"Found {len(search_results)} qualifying posts for '{query}'.")

            for post in tqdm(search_results, desc=f"Processing '{query}' posts"):
                post_reviews = extract_comments_from_post(post)
                all_reviews.extend(post_reviews)
                time.sleep(2) # Pause between processing posts
                    
        except Exception as e:
            print(f"Error during search for '{query}': {e}")
            
    return all_reviews



