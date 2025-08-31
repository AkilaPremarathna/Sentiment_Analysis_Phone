
import streamlit as st
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for black-light green theme with enhanced aesthetics
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* All text elements */
    .stApp, .stApp * {
        color: #ffffff !important;
        font-size: 22px !important; /* Increased font size */
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%);
        padding: 1.5rem; /* Reduced padding */
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 6px 8px rgba(50, 205, 50, 0.4);
    }
    
    .main-header h1 {
        font-size: 56px !important; /* Larger title */
        font-weight: bold !important;
        margin-bottom: 0.3rem !important;
    }
    
    .main-header p {
        font-size: 26px !important; /* Larger subtitle */
    }
    
    /* Section headings */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 32px !important; /* Larger headings */
    }
    
    /* Text input styling */
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a !important;
        border: 3px solid #90EE90 !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        font-size: 22px !important; /* Larger input text */
        color: #ffffff !important;
        height: 180px !important; /* Increased height */
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #32CD32 !important;
        box-shadow: 0 0 0 3px rgba(50, 205, 50, 0.4) !important;
        background-color: #222222 !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #888888 !important;
        font-size: 22px !important; /* Larger placeholder */
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 1rem 2.5rem !important; /* Adjusted padding */
        font-weight: bold !important;
        font-size: 24px !important; /* Larger button text */
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0.5rem 0 !important; /* Reduced margin */
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #228B22 0%, #90EE90 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 10px rgba(50, 205, 50, 0.5) !important;
    }
    
    /* Result containers */
    .positive-result {
        background: linear-gradient(135deg, #1a3d1a 0%, #2d5a2d 100%) !important;
        border-left: 6px solid #32CD32 !important;
        padding: 1.5rem !important; /* Reduced padding */
        border-radius: 15px !important;
        margin: 0.5rem 0 !important; /* Reduced margin */
        box-shadow: 0 4px 6px rgba(50, 205, 50, 0.4) !important;
    }
    
    .negative-result {
        background: linear-gradient(135deg, #3d1a1a 0%, #5a2d2d 100%) !important;
        border-left: 6px solid #FF6B6B !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 6px rgba(255, 107, 107, 0.4) !important;
    }
    
    .neutral-result {
        background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%) !important;
        border-left: 6px solid #6C757D !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 6px rgba(108, 117, 125, 0.4) !important;
    }
    
    /* Result text styling */
    .positive-result h3, .negative-result h3, .neutral-result h3 {
        font-size: 36px !important; /* Larger result title */
        font-weight: bold !important;
        margin-top: 0 !important;
    }
    
    .positive-result p, .negative-result p, .neutral-result p {
        font-size: 24px !important; /* Larger result text */
        font-weight: 500 !important;
    }
    
    /* Confidence bar */
    .confidence-bar {
        background-color: #333333 !important;
        height: 30px !important; /* Increased height */
        border-radius: 15px !important;
        overflow: hidden !important;
        margin: 1rem 0 !important;
        border: 2px solid #555555 !important;
    }
    
    .confidence-fill {
        height: 100% !important;
        background: linear-gradient(90deg, #32CD32, #90EE90) !important;
        border-radius: 15px !important;
        transition: width 0.3s ease !important;
    }
    
    /* Sidebar and other elements */
    .stSidebar {
        background-color: #111111 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 2px solid #32CD32 !important;
        border-radius: 10px !important;
        font-size: 24px !important; /* Larger expander text */
        font-weight: bold !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        border: 2px solid #333333 !important;
    }
    
    /* Chart styling */
    .stPlotlyChart {
        background-color: #1a1a1a !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #90EE90 !important;
        padding: 1.5rem; /* Reduced padding */
        border-top: 2px solid #333333;
        margin-top: 1rem; /* Reduced margin */
        font-size: 20px !important; /* Larger footer text */
    }
    
    /* Warning and info messages */
    .stAlert {
        background-color: #1a1a1a !important;
        border: 2px solid #32CD32 !important;
        color: #ffffff !important;
    }
    
    /* Spinner */
    .stSpinner {
        color: #32CD32 !important;
    }
    
    /* Hide streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load the trained models with caching for better performance"""
    try:
        model = joblib.load('Random_forest.joblib')
        vectorizer = joblib.load('tfidf_vectorizer.joblib')
        return model, vectorizer
    except FileNotFoundError:
        st.error("❌ Model files not found! Please ensure 'Random_forest.joblib' and 'tfidf_vectorizer.joblib' are in the app directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        st.stop()

def predict_sentiment(text, model, vectorizer):
    """Predict sentiment for given text"""
    try:
        # Transform text
        text_vectorized = vectorizer.transform([text.strip()])
        
        # Make prediction
        prediction = model.predict(text_vectorized)[0]
        probabilities = model.predict_proba(text_vectorized)[0]
        
        # Get confidence
        confidence = max(probabilities)
        
        # Map prediction to sentiment (adjust based on your model's output)
        sentiment_mapping = {
            0: "Negative",
            1: "Positive"
            # Add more mappings if you have multi-class classification
        }
        
        sentiment_label = sentiment_mapping.get(prediction, str(prediction))
        
        return sentiment_label, confidence, probabilities
        
    except Exception as e:
        st.error(f"❌ Prediction error: {str(e)}")
        return None, None, None

def display_result(sentiment, confidence, text):
    """Display the prediction result with styling"""
    
    if sentiment == "Positive":
        result_class = "positive-result"
        emoji = "😊"
        color = "#32CD32"
    elif sentiment == "Negative":
        result_class = "negative-result"
        emoji = "😞"
        color = "#FF6B6B"
    else:
        result_class = "neutral-result"
        emoji = "😐"
        color = "#6C757D"
    
    st.markdown(f"""
    <div class="{result_class}">
        <h3 style="margin-top: 0; color: {color};">
            {emoji} Sentiment: {sentiment}
        </h3>
        <p><strong>Confidence:</strong> {confidence:.2%}</p>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: {confidence*100}%;"></div>
        </div>
        <p><strong>Analyzed Text:</strong> "{text[:100]}{'...' if len(text) > 100 else ''}"</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎭 Sentiment Analyzer</h1>
        <p>Analyze the sentiment of your text using Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load models
    model, vectorizer = load_models()
    
    # Main content area
    col1, col2, col3 = st.columns([0.5, 6, 0.5])  # Adjusted column ratios
    
    with col2:
        st.markdown("### 📝 Enter your text for analysis:")
        
        # Text input
        user_text = st.text_area(
            "",
            height=180,
            placeholder="Type or paste your review, comment, or any text here...",
            help="Enter any text you want to analyze for sentiment",
            label_visibility="collapsed"
        )
        
        # Analyze button
        col_btn1, col_btn2, col_btn3 = st.columns([2, 3, 2])
        with col_btn2:
            analyze_button = st.button("🔍 Analyze Sentiment")
        
        # Process the text when button is clicked
        if analyze_button:
            if user_text.strip():
                with st.spinner("🤔 Analyzing sentiment..."):
                    sentiment, confidence, probabilities = predict_sentiment(user_text, model, vectorizer)
                    
                if sentiment:
                    display_result(sentiment, confidence, user_text)
                    
                    # Additional insights
                    st.markdown("---")
                    with st.expander("📊 View Detailed Analysis"):
                        # Create a simple chart for probabilities
                        if len(probabilities) == 2:  # Binary classification
                            prob_data = pd.DataFrame({
                                'Sentiment': ['Negative', 'Positive'],
                                'Probability': probabilities
                            })
                            st.bar_chart(prob_data.set_index('Sentiment'), color="#32CD32")
                        
                        # Display raw probabilities
                        st.write("**Probability Scores:**")
                        for i, prob in enumerate(probabilities):
                            sentiment_name = "Negative" if i == 0 else "Positive"
                            st.write(f"- {sentiment_name}: {prob:.4f}")
            else:
                st.warning("⚠️ Please enter some text to analyze!")
        
        # Example texts
        st.markdown("---")
        st.markdown("### 💡 Try these examples:")
        
        example_col1, example_col2 = st.columns(2)
        
        with example_col1:
            if st.button("👍 Positive Example", use_container_width=True, key="pos_btn"):
                st.text_area("Example:", "I absolutely love this product! It's amazing and works perfectly.", key="pos_example", disabled=True, height=80)
        
        with example_col2:
            if st.button("👎 Negative Example", use_container_width=True, key="neg_btn"):
                st.text_area("Example:", "This is terrible! I hate it and it doesn't work at all.", key="neg_example", disabled=True, height=80)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit and Machine Learning</p>
        <p>Powered by Random Forest Algorithm</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()