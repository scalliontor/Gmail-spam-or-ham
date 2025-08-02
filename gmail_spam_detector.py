import string
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import base64
import nltk
import re
from email.mime.text import MIMEText
import random
from collections import Counter

# Download NLTK data silently
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

class SimpleDataAugmentation:
    def __init__(self):
        try:
            from nltk.corpus import wordnet
            self.wordnet = wordnet
            self.spam_words = ['urgent', 'free', 'winner', 'prize', 'money', 'offer', 'deal']
        except:
            self.wordnet = None
            self.spam_words = []
    
    def get_synonyms(self, word):
        if not self.wordnet:
            return []
        try:
            synonyms = []
            for syn in self.wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym != word and synonym.isalpha():
                        synonyms.append(synonym)
            return synonyms[:3]  # Limit to 3
        except:
            return []
    
    def augment_text(self, words, label):
        if not words or len(words) < 3:
            return []
        
        try:
            new_versions = []
            for _ in range(2):
                new_words = words.copy()
                
                # Replace words with synonyms
                if random.random() < 0.5:
                    for i, word in enumerate(new_words):
                        if random.random() < 0.3:
                            synonyms = self.get_synonyms(word)
                            if synonyms:
                                new_words[i] = random.choice(synonyms)
                
                # Add spam words for spam texts
                if label == 'spam' and random.random() < 0.3 and self.spam_words:
                    spam_word = random.choice(self.spam_words)
                    new_words.insert(0, spam_word)
                
                if len(new_words) >= 3 and new_words != words:
                    new_versions.append(new_words)
            
            return new_versions
        except:
            return []

class GmailSpamDetector:
    def __init__(self):
        self.dataset_path = '2cls_spam_text_cls.csv'
        self.model_path = 'spam_detector_model.pkl'
        self.model = None
        self.dictionary = None
        self.label_encoder = None
        self.gmail_service = None
        self.gmail_scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        self.augmenter = SimpleDataAugmentation()
    
    def preprocess_text(self, text):
        try:
            # Clean and tokenize
            text = text.lower()
            text = text.translate(str.maketrans('', '', string.punctuation))
            words = nltk.word_tokenize(text)
            
            # Remove stop words and stem
            stop_words = set(nltk.corpus.stopwords.words('english'))
            words = [word for word in words if word not in stop_words and len(word) > 1]
            
            stemmer = nltk.PorterStemmer()
            words = [stemmer.stem(word) for word in words]
            
            return words
        except:
            return []
    
    def create_dictionary(self, all_messages):
        dictionary = []
        for words in all_messages:
            for word in words:
                if word not in dictionary:
                    dictionary.append(word)
        return dictionary
    
    def text_to_features(self, words):
        features = np.zeros(len(self.dictionary))
        for word in words:
            if word in self.dictionary:
                features[self.dictionary.index(word)] += 1
        return features
    
    def train_model(self, use_augmentation=True):
        try:
            # Load data
            df = pd.read_csv(self.dataset_path)
            messages = df['Message'].values.tolist()
            labels = df['Category'].values.tolist()
            
            # Preprocess
            processed_messages = [self.preprocess_text(msg) for msg in messages]
            
            # Augmentation
            if use_augmentation:
                augmented_messages, augmented_labels = [], []
                for message, label in zip(processed_messages, labels):
                    augmented_messages.append(message)
                    augmented_labels.append(label)
                    
                    # Add augmented versions
                    new_versions = self.augmenter.augment_text(message, label)
                    for new_version in new_versions:
                        augmented_messages.append(new_version)
                        augmented_labels.append(label)
                
                processed_messages, labels = augmented_messages, augmented_labels
            
            # Create features
            self.dictionary = self.create_dictionary(processed_messages)
            X = np.array([self.text_to_features(words) for words in processed_messages])
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(labels)
            
            # Train
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = MultinomialNB()
            self.model.fit(X_train, y_train)
            
            # Test
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            return accuracy
        except Exception as e:
            raise Exception(f"Training failed: {str(e)}")
    
    def save_model(self):
        try:
            model_data = {
                'model': self.model,
                'dictionary': self.dictionary,
                'label_encoder': self.label_encoder
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            return True
        except:
            return False
    
    def load_model(self):
        try:
            if not os.path.exists(self.model_path):
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.dictionary = model_data['dictionary']
            self.label_encoder = model_data['label_encoder']
            return True
        except:
            return False
    
    def predict_spam(self, text):
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            words = self.preprocess_text(text)
            features = self.text_to_features(words).reshape(1, -1)
            
            prediction = self.model.predict(features)[0]
            confidence = self.model.predict_proba(features)[0].max()
            label = self.label_encoder.inverse_transform([prediction])[0]
            
            return label, confidence
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
    
    def authenticate_gmail(self):
        try:
            creds = None
            
            # Load existing token
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.gmail_scopes)
            
            # Get new credentials if needed
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.gmail_scopes)
                    creds = flow.run_local_server(port=0, open_browser=True)
                
                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            # Create service
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.gmail_service.users().getProfile(userId='me').execute()  # Test connection
            return True
        except:
            return False
    
    def get_recent_emails(self, max_emails=20, days_back=7):
        try:
            if not self.gmail_service:
                return []
            
            # Get email list
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{date_filter}'
            
            results = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            email_data = []
            
            # Get email details
            for msg in messages:
                try:
                    email = self.gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
                    headers = email['payload'].get('headers', [])
                    
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    body = self.extract_email_body(email['payload'])
                    
                    email_data.append({
                        'id': msg['id'],
                        'subject': subject,
                        'sender': sender,
                        'body': body,
                        'full_text': f"{subject} {body}"
                    })
                except:
                    continue
            
            return email_data
        except:
            return []
    
    def extract_email_body(self, payload):
        try:
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
        except:
            return ""
    
    def extract_sender_info(self, sender):
        try:
            if '<' in sender and '>' in sender:
                name = sender.split('<')[0].strip()
                email_match = re.search(r'<([^>]+)>', sender)
                email = email_match.group(1) if email_match else sender
            else:
                name = "Friend"
                email = sender.strip()
            return name, email
        except:
            return "Friend", sender
    
    def create_rickroll_email(self, spammer_info, spam_subject):
        try:
            sender_name, sender_email = self.extract_sender_info(spammer_info)
            rickroll_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            # Default template if file doesn't exist
            template = ""      
            # Try to read custom template
            if os.path.exists('email.txt'):
                with open('email.txt', 'r', encoding='utf-8') as f:
                    template = f.read()

            # Fill template
            email_content = template.format(
                sender_name=sender_name,
                spam_subject=spam_subject,
                verify_link=rickroll_url
            )
            
            # Extract subject and body
            lines = email_content.split('\n')
            subject = "🚨 URGENT: Security Alert"
            body = email_content
            
            for line in lines:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                    body = '\n'.join(lines[lines.index(line)+1:]).strip()
                    break
            
            return subject, body, sender_email
        except:
            return "Security Alert", "Your email was flagged as spam.", spammer_info
    
    def send_counter_email(self, to_email, subject, body):
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            
            raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            sent = self.gmail_service.users().messages().send(userId='me', body=raw_message).execute()
            
            return True, sent['id']
        except Exception as e:
            return False, str(e)
    
    def scan_gmail_for_spam(self, max_emails=20, days_back=7):
        try:
            # Get emails
            emails = self.get_recent_emails(max_emails, days_back)
            if not emails:
                return [], []
            
            results = []
            counter_attacks = []
            
            # Check each email
            for email in emails:
                try:
                    prediction, confidence = self.predict_spam(email['full_text'])
                    
                    result = {
                        'id': email['id'],
                        'subject': email['subject'],
                        'sender': email['sender'],
                        'prediction': prediction,
                        'confidence': confidence,
                        'is_spam': prediction == 'spam'
                    }
                    results.append(result)
                    
                    # Prepare counter-attack for high-confidence spam
                    if prediction == 'spam' and confidence > 0.7:
                        sender_name, sender_email = self.extract_sender_info(email['sender'])
                        
                        # Skip system emails
                        skip_emails = ['noreply', 'no-reply', 'donotreply', 'mailer-daemon']
                        if not any(skip in sender_email.lower() for skip in skip_emails):
                            try:
                                subject, body, target = self.create_rickroll_email(email['sender'], email['subject'])
                                counter_attacks.append({
                                    'original_spam': result,
                                    'target_email': target,
                                    'subject': subject,
                                    'body': body
                                })
                            except:
                                continue
                except:
                    continue
            
            return results, counter_attacks
        except Exception as e:
            raise Exception(f"Scan failed: {str(e)}")
