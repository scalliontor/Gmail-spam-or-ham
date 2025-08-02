import string
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import base64
import nltk

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

class GmailSpamDetector:
    def __init__(self, dataset_path='2cls_spam_text_cls.csv'):
        self.dataset_path = dataset_path
        self.model = None
        self.dictionary = None
        self.le = None
        self.service = None
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def lowercase(self, text):
        return text.lower()

    def punctuation_removal(self, text):
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)

    def tokenize(self, text):
        return nltk.word_tokenize(text)

    def remove_stopwords(self, tokens):
        stop_words = nltk.corpus.stopwords.words('english')
        return [token for token in tokens if token not in stop_words]

    def stemming(self, tokens):
        stemmer = nltk.PorterStemmer()
        return [stemmer.stem(token) for token in tokens]

    def preprocess_text(self, text):
        text = self.lowercase(text)
        text = self.punctuation_removal(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.stemming(tokens)
        return tokens

    def create_dictionary(self, messages):
        dictionary = []
        for tokens in messages:
            for token in tokens:
                if token not in dictionary:
                    dictionary.append(token)
        return dictionary

    def create_features(self, tokens, dictionary):
        features = np.zeros(len(dictionary))
        for token in tokens:
            if token in dictionary:
                features[dictionary.index(token)] += 1
        return features

    def train_model(self):
        print("Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        messages = df['Message'].values.tolist()
        labels = df['Category'].values.tolist()
        
        print("Preprocessing data...")
        self.le = LabelEncoder()
        y = self.le.fit_transform(labels)
        
        processed_messages = [self.preprocess_text(message) for message in messages]
        self.dictionary = self.create_dictionary(processed_messages)
        X = np.array([self.create_features(tokens, self.dictionary) for tokens in processed_messages])
        
        print("Training model...")
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
        
        self.model = MultinomialNB()
        self.model.fit(X_train, y_train)
        
        y_val_pred = self.model.predict(X_val)
        val_accuracy = accuracy_score(y_val, y_val_pred)
        
        print(f'Validation accuracy: {val_accuracy:.4f}')
        print("Model training completed!")
        
        return val_accuracy

    def save_model(self, model_path='spam_detector_model.pkl'):
        model_data = {
            'model': self.model,
            'dictionary': self.dictionary,
            'label_encoder': self.le
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {model_path}")

    def load_model(self, model_path='spam_detector_model.pkl'):
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.model = model_data['model']
            self.dictionary = model_data['dictionary']
            self.le = model_data['label_encoder']
            print(f"Model loaded from {model_path}")
            return True
        else:
            print(f"Model file {model_path} not found")
            return False

    def predict_spam(self, text):
        if self.model is None or self.dictionary is None:
            raise ValueError("Model not trained or loaded.")
        
        processed_text = self.preprocess_text(text)
        features = self.create_features(processed_text, self.dictionary)
        features = np.array(features).reshape(1, -1)
        prediction = self.model.predict(features)
        prediction_proba = self.model.predict_proba(features)
        prediction_cls = self.le.inverse_transform(prediction)[0]
        confidence = np.max(prediction_proba)
        
        return prediction_cls, confidence

    def authenticate_gmail(self, credentials_file='credentials.json', token_file='token.json'):
        """Authenticate with Gmail API - optimized for auto-authentication"""
        creds = None
        
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            except:
                # If token is corrupted, delete it and re-authenticate
                os.remove(token_file)
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    creds = None
            
            if not creds:
                if not os.path.exists(credentials_file):
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.SCOPES)
                    # Use a more robust port handling
                    try:
                        creds = flow.run_local_server(port=8080, open_browser=True)
                    except:
                        # Try alternative port if 8080 is busy
                        creds = flow.run_local_server(port=0, open_browser=True)
                except:
                    return False
            
            # Save credentials for next run
            try:
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            except:
                pass  # Continue even if we can't save token
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            # Test the connection
            self.service.users().getProfile(userId='me').execute()
            return True
        except:
            return False

    def get_gmail_messages(self, max_results=10, days_back=7):
        if self.service is None:
            return []
        
        try:
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date}'
            
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                return []
            
            detailed_messages = []
            for msg in messages:
                message = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                body = self.extract_message_body(message['payload'])
                
                detailed_messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'full_text': f"{subject} {body}"
                })
            
            return detailed_messages
            
        except HttpError:
            return []

    def extract_message_body(self, payload):
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body

    def check_gmail_spam(self, max_results=10, days_back=7):
        if self.model is None or self.service is None:
            return []
        
        messages = self.get_gmail_messages(max_results, days_back)
        results = []
        
        print(f"Analyzing {len(messages)} messages...")
        
        for i, msg in enumerate(messages, 1):
            prediction, confidence = self.predict_spam(msg['full_text'])
            
            result = {
                'message_id': msg['id'],
                'subject': msg['subject'],
                'sender': msg['sender'],
                'prediction': prediction,
                'confidence': confidence,
                'is_spam': prediction == 'spam'
            }
            results.append(result)
            
            status = "SPAM" if prediction == 'spam' else "HAM"
            print(f"{i}. {status} ({confidence:.3f}) - {msg['subject'][:50]}")
        
        spam_count = sum(1 for r in results if r['is_spam'])
        print(f"Found {spam_count}/{len(results)} spam messages")
        
        return results

def main():
    detector = GmailSpamDetector()
    
    if not detector.load_model():
        detector.train_model()
        detector.save_model()
    
    if detector.authenticate_gmail():
        detector.check_gmail_spam(max_results=10, days_back=7)

if __name__ == "__main__":
    main()
