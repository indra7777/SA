import pandas as pd
import nltk
import os

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Ensure the input is a string
    if not isinstance(text, str):
        text = str(text)
    # Tokenize text
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [word for word in tokens if word.lower() not in stopwords]
    # Join tokens back into a single string
    return ' '.join(tokens)

# Print current working directory
print("Current working directory:", os.getcwd())

# Check if the dataset file exists
dataset_path = './dataset/Dataset-SA.csv'
print(f"Checking if dataset file exists at: {dataset_path}")
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

# Load dataset
data = pd.read_csv(dataset_path)

# Convert 'Rate' column to numeric
data['Rate'] = pd.to_numeric(data['Rate'], errors='coerce')

# Preprocess review text
data['Review'] = data['Review'].apply(preprocess_text)

# Map overall ratings to sentiment labels
def map_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating == 3:
        return 'neutral'
    else:
        return 'negative'

data['label'] = data['Rate'].apply(map_sentiment)

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Save preprocessed data
data.to_csv('trained_data/preprocessed_reviews.csv', index=False)