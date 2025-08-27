# 🎭 Sentiment Analyzer  

A **Streamlit-based web application** for analyzing text sentiment using a **Random Forest Classifier** and **TF-IDF Vectorizer**.  
The app provides real-time predictions with confidence scores and interactive visualizations.  

---

## 🌟 Overview  

This project provides a clean and interactive interface for sentiment analysis. It uses **Machine Learning** to classify text as Positive or Negative.  

The key components of this project include:  

- 🚀 **app.py**: Main Streamlit application script.  
- 🧠 **Random_forest.joblib**: Trained Random Forest model for sentiment classification.  
- ✍️ **tfidf_vectorizer.joblib**: TF-IDF vectorizer used for feature extraction.  
- 📦 **requirements.txt**: Contains all required dependencies.  

---

## ✨ Features  

- 🔍 **Sentiment Prediction** – Classifies text as **Positive** 😊 or **Negative** 😞  
- 📊 **Confidence Score** – Shows prediction confidence with progress bar  
- 🌑 **Dark Black + Light Green Theme** – Modern styled UI for better readability  
- 📈 **Detailed Analysis** – Expandable view with probability distribution bar chart  
- 💡 **Example Inputs** – Preloaded positive & negative example texts  

---

## 🛠️ Tech Stack  

- [Streamlit](https://streamlit.io/) – Frontend & UI  
- [Scikit-learn](https://scikit-learn.org/) – Random Forest Classifier  
- [Joblib](https://joblib.readthedocs.io/) – Model serialization  
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) – Data handling  
- [TF-IDF Vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) – Text feature extraction  

---


📁 Sentiment-Analyzer
│── app.py # Main Streamlit app
│── Random_forest.joblib # Trained Random Forest model
│── tfidf_vectorizer.joblib # Trained TF-IDF vectorizer
│── requirements.txt # Dependencies
│── README.md # Project documentation



🧪 Example Usage
Input:
I absolutely love this product! It's amazing and works perfectly.

Output:

Sentiment: Positive 😊

Confidence: 95%

## 📂 Project Structure  

