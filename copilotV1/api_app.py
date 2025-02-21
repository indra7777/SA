from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load the trained model and vectorizer
model = joblib.load('../models/sentiment_model.pkl')
vectorizer = joblib.load('../models/vectorizer.pkl')

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