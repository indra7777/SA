from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import os
import logging
from scraping.flipkart import scrape_flipkart_reviews
from scraping.dell import scrape_dell_product
from scraping.Nykaa import scrape_nykaa_product
from scraping.nike import scrape_nike_product
from scraping.Myntra import scrape_myntra_product
import pandas as pd

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

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

@app.route('/scrape/dell', methods=['GET'])
def scrape_dell():
    product_url = request.args.get('url')
    if not product_url:
        logger.error("URL parameter is required")
        return jsonify({'error': 'URL parameter is required'}), 400
    
    if not product_url.startswith('https://www.dell.com'):
        logger.error("Invalid Dell URL")
        return jsonify({'error': 'Invalid Dell URL. Must be a Dell product URL'}), 400
    
    logger.info(f"Scraping Dell product from URL: {product_url}")
    
    try:
        # Scrape the Dell product details and reviews
        filename = scrape_dell_product(product_url)
        
        if not filename:
            return jsonify({'error': 'Failed to scrape product data'}), 500
        
        # Read the CSV file and process the data
        df = pd.read_csv(filename)
        
        # Process reviews if they exist
        reviews = df['review_text'].tolist()
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for review in reviews:
            if review != 'No Reviews':
                processed_text = preprocess_text(review)
                text_vector = vectorizer.transform([processed_text])
                prediction = model.predict(text_vector)[0]
                sentiment_counts[prediction] += 1
        
        response_data = {
            'product_title': df['product_title'].iloc[0],
            'product_images': df['product_images'].iloc[0].split(', '),
            'specifications': df['specifications'].iloc[0].split(', '),
            'sentiment_analysis': sentiment_counts,
            'total_reviews': len(reviews) if reviews[0] != 'No Reviews' else 0,
            'csv_file': filename
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error scraping Dell product: {str(e)}")
        return jsonify({'error': f'Error scraping product: {str(e)}'}), 500

@app.route('/scrape/nykaa', methods=['GET'])
def scrape_nykaa():
    product_url = request.args.get('url')
    if not product_url:
        logger.error("URL parameter is required")
        return jsonify({'error': 'URL parameter is required'}), 400
    
    if not product_url.startswith('https://www.nykaa.com'):
        logger.error("Invalid Nykaa URL")
        return jsonify({'error': 'Invalid Nykaa URL. Must be a Nykaa product URL'}), 400
    
    logger.info(f"Scraping Nykaa product from URL: {product_url}")
    
    try:
        # Scrape the Nykaa product details and reviews
        filename = scrape_nykaa_product(product_url)
        
        if not filename:
            return jsonify({'error': 'Failed to scrape product data'}), 500
        
        # Read the CSV file and process the data
        df = pd.read_csv(filename)
        
        # Process reviews if they exist
        reviews = df['review_text'].tolist()
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for review in reviews:
            if review != 'No Reviews':
                processed_text = preprocess_text(review)
                text_vector = vectorizer.transform([processed_text])
                prediction = model.predict(text_vector)[0]
                sentiment_counts[prediction] += 1
        
        # Convert numpy.int64 to regular Python int
        response_data = {
            'product_title': df['product_title'].iloc[0],
            'image_url': df['image_url'].iloc[0],
            'description': df['description'].iloc[0],
            'total_ratings': int(df['total_ratings'].iloc[0]),  # Convert to Python int
            'total_reviews': int(df['total_reviews'].iloc[0]),  # Convert to Python int
            'sentiment_analysis': {
                'positive': int(sentiment_counts['positive']),
                'neutral': int(sentiment_counts['neutral']),
                'negative': int(sentiment_counts['negative'])
            },
            'total_reviews_analyzed': int(len(reviews)) if reviews[0] != 'No Reviews' else 0,
            'csv_file': filename
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error scraping Nykaa product: {str(e)}")
        return jsonify({'error': f'Error scraping product: {str(e)}'}), 500

@app.route('/scrape/nike', methods=['GET'])
def scrape_nike():
    product_url = request.args.get('url')
    if not product_url:
        logger.error("URL parameter is required")
        return jsonify({'error': 'URL parameter is required'}), 400
    if not product_url.startswith('https://www.nike.com'):
        logger.error("Invalid Nike URL")
        return jsonify({'error': 'Invalid Nike URL. Must be a Nike product URL'}), 400
    logger.info(f"Scraping Nike product from URL: {product_url}")
    try:
        filename = scrape_nike_product(product_url)
        if not filename:
            return jsonify({'error': 'Failed to scrape product data'}), 500
        df = pd.read_csv(filename)
        reviews = df['review_text'].tolist()
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for review in reviews:
            if review != 'No Reviews':
                processed_text = preprocess_text(review)
                text_vector = vectorizer.transform([processed_text])
                prediction = model.predict(text_vector)[0]
                sentiment_counts[prediction] += 1
        # Try to get product details from the product details CSV if available
        product_details_file = filename.replace('reviews', 'details')
        if os.path.exists(product_details_file):
            df_product = pd.read_csv(product_details_file)
            product_title = df_product['product_title'].iloc[0] if 'product_title' in df_product.columns else ''
            image_url = df_product['image_url'].iloc[0] if 'image_url' in df_product.columns else ''
            price = df_product['price'].iloc[0] if 'price' in df_product.columns else ''
            description = df_product['description'].iloc[0] if 'description' in df_product.columns else ''
        else:
            product_title = image_url = price = description = ''
        response_data = {
            'product_title': product_title,
            'image_url': image_url,
            'price': price,
            'description': description,
            'sentiment_analysis': {
                'positive': int(sentiment_counts['positive']),
                'neutral': int(sentiment_counts['neutral']),
                'negative': int(sentiment_counts['negative'])
            },
            'total_reviews_analyzed': int(len(reviews)) if reviews and reviews[0] != 'No Reviews' else 0,
            'csv_file': filename
        }
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error scraping Nike product: {str(e)}")
        return jsonify({'error': f'Error scraping product: {str(e)}'}), 500

@app.route('/scrape/myntra', methods=['GET'])
def scrape_myntra():
    product_url = request.args.get('url')
    if not product_url:
        logger.error("URL parameter is required")
        return jsonify({'error': 'URL parameter is required'}), 400
    if not product_url.startswith('https://www.myntra.com'):
        logger.error("Invalid Myntra URL")
        return jsonify({'error': 'Invalid Myntra URL. Must be a Myntra product URL'}), 400
    logger.info(f"Scraping Myntra product from URL: {product_url}")
    try:
        filename = scrape_myntra_product(product_url)
        if not filename:
            return jsonify({'error': 'Failed to scrape product data'}), 500
        df = pd.read_csv(filename)
        reviews = df['review_text'].tolist()
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for review in reviews:
            if review != 'No Reviews':
                processed_text = preprocess_text(review)
                text_vector = vectorizer.transform([processed_text])
                prediction = model.predict(text_vector)[0]
                sentiment_counts[prediction] += 1
        # Try to get product details from the product details CSV if available
        product_details_file = filename.replace('reviews', 'data')
        if os.path.exists(product_details_file):
            # Read as key-value pairs
            df_product = pd.read_csv(product_details_file)
            product_title = df_product[df_product['Field'] == 'product_title']['Value'].values[0] if 'product_title' in df_product['Field'].values else ''
            image_urls = df_product[df_product['Field'] == 'image_urls']['Value'].values[0] if 'image_urls' in df_product['Field'].values else ''
            product_details = df_product[df_product['Field'] == 'product_details']['Value'].values[0] if 'product_details' in df_product['Field'].values else ''
        else:
            product_title = image_urls = product_details = ''
        response_data = {
            'product_title': product_title,
            'image_urls': image_urls,
            'product_details': product_details,
            'sentiment_analysis': {
                'positive': int(sentiment_counts['positive']),
                'neutral': int(sentiment_counts['neutral']),
                'negative': int(sentiment_counts['negative'])
            },
            'total_reviews_analyzed': int(len(reviews)) if reviews and reviews[0] != 'No Reviews' else 0,
            'csv_file': filename
        }
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error scraping Myntra product: {str(e)}")
        return jsonify({'error': f'Error scraping product: {str(e)}'}), 500

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
    app.run(host='0.0.0.0', port=5050, debug=True)
