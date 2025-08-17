# gemini_analyzer.py

import os
import google.generativeai as genai
import json

# --- NEW, MORE ROBUST STRUCTURE ---

def setup_gemini(api_key: str):
    """
    Configures the Gemini API with the provided key.
    This function should be called once at the start of the application.
    """
    if not api_key:
        print("❌ Error: Gemini API key is missing.")
        print("Please provide a valid GOOGLE_API_KEY.")
        exit()
    
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API connection successful.")
    except Exception as e:
        print(f"❌ An error occurred while configuring the Gemini API: {e}")
        exit()

# --- THE REST OF THE FILE REMAINS THE SAME ---

def create_gemini_prompt(post_title: str, comment_text: str) -> str:
    """Creates a detailed prompt for the Gemini model."""
    
    prompt = f"""
    You are an expert phone review analyst. Your task is to analyze a Reddit comment about a smartphone and extract specific details in a structured JSON format.

    **Instructions:**
    1.  Read the **Post Title** and **Comment Body** carefully.
    2.  Identify the specific **phone model** being discussed. Be precise (e.g., "iPhone 15 Pro Max", not just "iPhone").
    3.  Based on the sentiment and content of the comment, infer a **rating** on a scale of 1 to 5 (1=Very Negative, 5=Very Positive).
    4.  Extract the core aspects of the phone the user is reviewing, such as **battery, screen, camera, performance, and build quality**.
    5.  Do NOT invent any information. If a detail cannot be found, use "N/A".
    6.  The final output MUST be a valid JSON object.

    **Post Title:** "{post_title}"
    **Comment Body:** "{comment_text}"

    **JSON Output Format:**
    {{
      "phone_model": "Exact Phone Model",
      "rating": <inferred integer rating 1-5>,
      "review_summary": {{
        "battery": "User's opinion on the battery",
        "camera": "User's opinion on the camera",
        "screen": "User's opinion on the screen",
        "performance": "User's opinion on the performance",
        "design_build": "User's opinion on the design and build quality",
        "long_term_issues": "Mention of any issues after long-term use (e.g., after 5 years)"
      }}
    }}
    """
    return prompt

def analyze_review_with_gemini(post_title: str, comment_text: str) -> dict:
    """
    Analyzes review text using Gemini Flash and returns structured data.
    """
    if not post_title and not comment_text:
        return {}

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = create_gemini_prompt(post_title, comment_text)
        
        response = model.generate_content(prompt)
        
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        
        return json.loads(cleaned_response)
        
    except json.JSONDecodeError:
        # Adding a print statement here for better debugging
        # print(f"Warning: Gemini returned a non-JSON response: {response.text}")
        return {}
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return {}