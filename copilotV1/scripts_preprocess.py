import pandas as pd
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Tokenize text
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [word for word in tokens if word.lower() not in stopwords]
    # Join tokens back into a single string
    return ' '.join(tokens)

# Load dataset
data = pd.read_csv('data/amazon_reviews.csv')

# Preprocess review text
data['reviewText'] = data['reviewText'].apply(preprocess_text)

# Map overall ratings to sentiment labels
def map_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating == 3:
        return 'neutral'
    else:
        return 'negative'

data['label'] = data['overall'].apply(map_sentiment)

# Save preprocessed data
data.to_csv('data/preprocessed_reviews.csv', index=False)