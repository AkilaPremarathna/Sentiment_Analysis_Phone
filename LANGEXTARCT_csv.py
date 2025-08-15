import os
import pandas as pd
import langextract as lx
import textwrap
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

def format_extraction_results(extractions):
    """Format the extraction results into a single string for CSV storage"""
    result_parts = []
    
    for extraction in extractions:
        part = f"Class: {extraction.extraction_class}\n"
        part += f"Text: '{extraction.extraction_text}'"
        if extraction.attributes:
            part += f"\nAttributes: {extraction.attributes}"
        result_parts.append(part)
    
    return "\n------------------------------\n".join(result_parts)

def analyze_sentiment(text, prompt, examples, api_key):
    """Perform sentiment analysis on a single text"""
    try:
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
            api_key=api_key
        )
        return format_extraction_results(result.extractions)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not found!")
        print("Please set your Google API key using one of these methods:")
        print("1. export GOOGLE_API_KEY='your-api-key-here'")
        print("2. Create a .env file with: GOOGLE_API_KEY=your-api-key-here")
        return
    
    # Get CSV file path from user
    csv_file_path = input("Enter the path to your CSV file: ").strip()
    
    if not os.path.exists(csv_file_path):
        print(f"Error: File '{csv_file_path}' not found!")
        return
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Successfully loaded CSV with {len(df)} rows")
        
        # Check if 'review_text' column exists
        if 'review_text' not in df.columns:
            print(f"Error: 'review_text' column not found in CSV!")
            print(f"Available columns: {list(df.columns)}")
            return
        
        print(f"Found {len(df)} reviews to analyze...")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Define the prompt and extraction rules
    prompt = textwrap.dedent("""\
        Extract aspects, opinions, and specific feature details from the smartphone review in order of appearance.
    - 'aspect' refers to a specific component or feature of the phone (e.g., 'camera', 'battery life', 'price').
    - 'opinion' refers to the user's subjective feeling or judgment about an aspect (e.g., 'is impressive', 'great', 'is a downside').
    - 'feature_detail' refers to a specific capability mentioned (e.g., 'fast charging').

    Use exact text for all extractions. Do not paraphrase or overlap entities.
    For each 'opinion' extracted, add a 'sentiment' attribute with the value 'positive', 'negative', or 'neutral'.""")

    # High-quality examples to guide the model for smartphone reviews
    examples = [
        # Example 1: A review with multiple positive aspects
        lx.data.ExampleData(
            text="The camera takes amazing photos and the battery lasts all day.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="camera",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="takes amazing photos",
                    attributes={"sentiment": "positive"}
                ),
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="battery",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="lasts all day",
                    attributes={"sentiment": "positive"}
                ),
            ]
        ),

        # Example 2: A mixed review with positive and negative points
        lx.data.ExampleData(
            text="Love the display and performance, but the high price is a major downside.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="Love",
                    attributes={"sentiment": "positive"}
                ),
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="display",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="performance",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="price",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="is a major downside",
                    attributes={"sentiment": "negative"}
                ),
            ]
        ),

        # Example 3: A review mentioning a specific feature detail
        lx.data.ExampleData(
            text="Great value for money. The build quality feels premium and fast charging is a nice bonus.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="value for money",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="Great",
                    attributes={"sentiment": "positive"}
                ),
                lx.data.Extraction(
                    extraction_class="aspect",
                    extraction_text="build quality",
                    attributes={}
                ),
                lx.data.Extraction(
                    extraction_class="opinion",
                    extraction_text="feels premium",
                    attributes={"sentiment": "positive"}
                ),
                lx.data.Extraction(
                    extraction_class="feature_detail",
                    extraction_text="fast charging",
                    attributes={}
                ),
            ]
        )
    ]

    # Create a new column for sentiment analysis results
    sentiment_results = []
    
    print("Starting sentiment analysis...")
    print("=" * 50)
    
    for index, row in df.iterrows():
        review_text = row['review_text']
        
        # Skip empty or NaN reviews
        if pd.isna(review_text) or str(review_text).strip() == '':
            sentiment_results.append("No review text")
            continue
        
        print(f"Processing review {index + 1}/{len(df)}: {str(review_text)[:50]}...")
        
        # Perform sentiment analysis
        result = analyze_sentiment(review_text, prompt, examples, api_key)
        sentiment_results.append(result)
        
        # Print result for current review
        print(f"Results for review {index + 1}:")
        print(result)
        print("-" * 50)
    
    # Add sentiment analysis results to dataframe
    df['sentiment_analysis'] = sentiment_results
    
    # Save results to new CSV file
    output_file = csv_file_path.replace('.csv', '_with_sentiment.csv')
    df.to_csv(output_file, index=False)
    
    print(f"\nSentiment analysis completed!")
    print(f"Results saved to: {output_file}")
    print(f"Processed {len(df)} reviews successfully.")

if __name__ == "__main__":
    main()