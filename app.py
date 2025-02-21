from flask import Flask, request, jsonify, send_from_directory
import joblib
import os
import logging
from scraping.flipkart import scrape_flipkart_reviews
import pandas as pd

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model and vectorizer
model = joblib.load('models/sentiment_model.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    review_text = data['review']
    
    # Preprocess the review text
    processed_text = preprocess_text(review_text)
    
    # Vectorize the text
    text_vector = vectorizer.transform([processed_text])
    
    # Predict the sentiment
    prediction = model.predict(text_vector)
    
    return jsonify({'sentiment': prediction[0]})

@app.route('/scrape', methods=['GET'])
def scrape():
    product_url = request.args.get('url')
    if not product_url:
        logger.error("URL parameter is required")
        return jsonify({'error': 'URL parameter is required'}), 400
    
    logger.info(f"Scraping reviews from URL: {product_url}")
    
    # Scrape the Flipkart product reviews
    filename = scrape_flipkart_reviews(product_url)
    
    # Preprocess and predict sentiments for each review
    reviews = get_reviews_from_csv(filename)
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for review in reviews:
        processed_text = preprocess_text(review)
        text_vector = vectorizer.transform([processed_text])
        prediction = model.predict(text_vector)[0]
        
        if prediction == 'positive':
            sentiment_counts['positive'] += 1
        elif prediction == 'neutral':
            sentiment_counts['neutral'] += 1
        elif prediction == 'negative':
            sentiment_counts['negative'] += 1
    
    total_reviews = len(reviews)
    sentiment_percentages = {
        'positive': (sentiment_counts['positive'] / total_reviews) * 100,
        'neutral': (sentiment_counts['neutral'] / total_reviews) * 100,
        'negative': (sentiment_counts['negative'] / total_reviews) * 100
    }
    
    logger.info(f"Sentiment percentages: {sentiment_percentages}")
    
    return jsonify(sentiment_percentages)

def get_reviews_from_csv(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Extract the 'Review' column and convert it to a list
    reviews = df['Review'].tolist()
    
    return reviews

def preprocess_text(text):
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    
    # Tokenize text
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [word for word in tokens if word.lower() not in stopwords]
    # Join tokens back into a single string
    return ' '.join(tokens)

if __name__ == '__main__':
    app.run(debug=True)
