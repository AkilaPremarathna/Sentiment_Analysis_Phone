🎭 #Sentiment Analyzer

A Streamlit-based web application that analyzes the sentiment of user-provided text (reviews, comments, feedback, etc.) using a Random Forest Machine Learning model and TF-IDF vectorizer.

The app provides real-time predictions with a confidence score, beautiful UI, and interactive visualization of sentiment probabilities.

🚀 Features

🌑 Dark Black + Light Green Themed UI

📝 Text Input Area – Enter any text for analysis

🔍 Sentiment Prediction – Detects Positive or Negative sentiment

📊 Confidence Bar & Probabilities – Shows prediction confidence visually

📈 Detailed Analysis (Expandable) – View probability distribution in a bar chart

💡 Example Inputs – Try sample positive and negative text snippets

⚡ Optimized with Model Caching for faster performance

🛠️ Tech Stack

Streamlit
 – Frontend & UI

Scikit-learn
 – Machine Learning (Random Forest)

Joblib
 – Model serialization

Pandas
 & NumPy
 – Data handling

TF-IDF Vectorizer
 – Text feature extraction

📂 Project Structure
📁 Sentiment-Analyzer
│── Random_forest.joblib           # Trained Random Forest model
│── tfidf_vectorizer.joblib        # Trained TF-IDF vectorizer
│── app.py                         # Main Streamlit app
│── requirements.txt               # Dependencies
│── README.md                      # Project documentation

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/Sentiment-Analyzer.git
cd Sentiment-Analyzer

2️⃣ Create Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Model Files

Place the following files in the root directory:

Random_forest.joblib

tfidf_vectorizer.joblib

▶️ Run the Application
streamlit run app.py


Then, open your browser and go to:
👉 http://localhost:8501

📸 Screenshots
Main UI

Sentiment Result Example

🧪 Example Usage
Input:
I absolutely love this product! It's amazing and works perfectly.

Output:

Sentiment: Positive 😊

Confidence: 95%

🛡️ Error Handling

If model/vectorizer files are missing → ❌ Error message shown

If empty text is entered → ⚠️ Warning to provide input

❤️ Acknowledgements

Built with Streamlit

Powered by Random Forest Algorithm

Inspired by real-world Sentiment Analysis use-cases

📜 License

This project is open-source and available under the MIT License.
