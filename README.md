Sentiment Analyzer

A web-based application built with Streamlit to analyze the sentiment of user-provided text using a Random Forest Machine Learning model. The app features a sleek black and green aesthetic, enhanced font sizes, and an optimized layout for better usability. It predicts whether the sentiment is Positive or Negative and provides confidence scores.

Features





Sentiment Analysis: Analyze text input (reviews, comments, etc.) using a pre-trained Random Forest model.



Confidence Visualization: Displays a confidence bar and probability scores for the prediction.



Example Inputs: Includes pre-defined Positive and Negative examples for quick testing.



Responsive Design: Optimized UI with larger fonts and reduced blank spaces for an aesthetic experience.



Detailed Insights: Expandable section with a bar chart of probability scores.

Requirements





Python 3.8+



Required Python packages (listed in requirements.txt):





streamlit



joblib



numpy



pandas



scikit-learn

Installation

Prerequisites





Install Python 3.8 or higher from python.org.



Install Git from git-scm.com if you plan to use version control.

Steps to Run Locally





Clone the Repository





Open a terminal and run:

git clone https://github.com/yourusername/sentiment-analyzer.git
cd sentiment-analyzer



Install Dependencies





Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



Install required packages:

pip install -r requirements.txt



Prepare Model Files





Ensure the pre-trained model files (Random_forest.joblib and tfidf_vectorizer.joblib) are placed in the project directory. These files are required for the app to function and should be generated from your training pipeline.



Run the App





Start the Streamlit app:

streamlit run app.py



Open your browser and navigate to http://localhost:8501 to use the app.

Usage





Enter Text: Type or paste your text (e.g., a review or comment) into the text area.



Analyze: Click the "Analyze Sentiment" button to get the prediction.



View Results: The app displays the sentiment (Positive/Negative), confidence level, and an optional detailed analysis with probability scores.



Try Examples: Use the "Positive Example" or "Negative Example" buttons to test with pre-loaded text.
