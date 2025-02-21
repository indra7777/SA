# How It Works

This document provides a detailed explanation of how the Amazon product review analysis project works. It covers data preprocessing, feature extraction, model training, evaluation, and serving the model using a Flask API.

## 1. Data Preprocessing

Data preprocessing is a crucial step in preparing the text data for machine learning. This includes tokenization, stopword removal, text normalization, and mapping ratings to sentiment labels.

### Tokenization
Tokenization is the process of splitting the text into individual words or tokens. This is done using the NLTK library's `word_tokenize` function.

```python
tokens = nltk.word_tokenize(text)
```

### Stopword Removal
Stopwords are common words that do not carry significant meaning and can be removed to reduce the dimensionality of the data. The NLTK library provides a list of English stopwords which can be used for this purpose.

```python
stopwords = nltk.corpus.stopwords.words('english')
tokens = [word for word in tokens if word.lower() not in stopwords]
```

### Text Normalization
Text normalization involves converting the tokens back into a single string after processing.

```python
processed_text = ' '.join(tokens)
```

### Mapping Ratings to Sentiment Labels
Amazon product ratings are mapped to sentiment labels (positive, neutral, negative) based on the overall rating.

```python
def map_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating == 3:
        return 'neutral'
    else:
        return 'negative'

data['label'] = data['overall'].apply(map_sentiment)
```

## 2. Feature Extraction

Feature extraction is the process of converting the text data into numerical features that can be used by the machine learning model. This is done using the `CountVectorizer` from scikit-learn, which converts the text into a bag-of-words representation.

```python
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)
```

## 3. Model Training

The machine learning model used in this project is the Naive Bayes classifier. This is a simple yet effective algorithm for text classification tasks. The model is trained using the vectorized training data.

```python
model = MultinomialNB()
model.fit(X_train_vec, y_train)
```

## 4. Model Evaluation

After training the model, it is evaluated on the test set to determine its performance. The evaluation metrics used are accuracy and the classification report which includes precision, recall, and F1-score.

### Accuracy
Accuracy is the ratio of correctly predicted instances to the total instances.

```python
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy}')
```

### Classification Report
The classification report provides detailed metrics for each class (positive, negative, neutral), including precision, recall, and F1-score.

```python
report = classification_report(y_test, y_pred)
print('Classification Report:')
print(report)
```

## 5. Serving the Model with Flask API

To make the sentiment analysis model available for production use, a REST API is created using Flask. The API accepts POST requests with review text and returns the predicted sentiment.

### API Endpoint
The `/predict` endpoint accepts JSON data with a `review` field, preprocesses the review text, vectorizes it, and uses the trained model to predict the sentiment.

```python
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
```

### Running the API
To start the API server, run the `app.py` script in the `api` directory.

```bash
cd api
python app.py
```

### Making Predictions
Send a POST request to the `/predict` endpoint with the review text to get the sentiment prediction.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"review": "I love this product!"}' http://127.0.0.1:5000/predict
```

## Summary

1. **Data Preprocessing**: Tokenize the text, remove stopwords, normalize the text, and map ratings to sentiment labels.
2. **Feature Extraction**: Convert the text data into numerical features using `CountVectorizer`.
3. **Model Training**: Train a Naive Bayes classifier using the vectorized training data.
4. **Model Evaluation**: Evaluate the model's performance using accuracy and the classification report.
5. **Serving the Model**: Create a Flask API to serve the trained model and make predictions on new reviews.

By following these steps, the Amazon product review analysis project can effectively classify reviews into positive, negative, and neutral sentiments, and provide predictions via a REST API.