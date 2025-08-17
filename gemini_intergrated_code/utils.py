import csv

def save_to_csv(reviews_data, filename="phone_reviews_final.csv"):
    """Save reviews data to CSV file."""
    if not reviews_data:
        print("No reviews data to save.")
        return

    # Define the headers for the CSV file
    fieldnames = [
        'review_id', 'phone_category', 'product_id', 'review_text', 
        'rating', 'review_date', 'helpful_votes', 'total_votes', 
        'reviewer_name', 'battery_review', 'camera_review', 
        'screen_review', 'performance_review', 'design_build_review',
        'long_term_review'
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews_data)
        
        print(f"✓ Successfully saved {len(reviews_data)} reviews to {filename}")

    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")