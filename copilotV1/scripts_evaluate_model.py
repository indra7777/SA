import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load preprocessed dataset
data = pd.read_csv('data/preprocessed_reviews.csv')

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data['reviewText'], data['label'], test_size=0.2, random_state=42)

# Load the trained model and vectorizer
model = joblib.load('models/sentiment_model.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

# Vectorize text data
X_test_vec = vectorizer.transform(X_test)

# Make predictions on the test set
y_pred = model.predict(X_test_vec)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f'Accuracy: {accuracy}')
print('Classification Report:')
print(report)