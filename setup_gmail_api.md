# Gmail API Setup Guide

## 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

## 2. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Download the JSON file
5. Rename it to `credentials.json` and place it in your project folder

## 3. **IMPORTANT: Configure OAuth Consent Screen (New Step)**

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace account)
3. Fill in the required fields:
   - App name: "Spam Detector"
   - User support email: your email
   - Developer contact information: your email
4. **Add Test Users**:
   - In the "Test users" section, click "ADD USERS"
   - Add your Gmail address (sitdowntakeasip@gmail.com)
   - Add any other Gmail addresses you want to test with
5. Save the configuration

## 4. Alternative: Use Internal User Type (If Available)

If you have a Google Workspace account:
1. Choose "Internal" user type instead
2. This will only work with emails from your organization
3. No verification process needed

## 5. Install Dependencies

### Option 1: Using the installation script (Recommended)
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Option 2: Manual installation
```bash
# Install testresources first to fix dependency conflicts
pip install testresources

# Install other dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"
```

### Option 3: If you still have issues
```bash
# Create a virtual environment (recommended)
python -m venv spam_detector_env
source spam_detector_env/bin/activate  # On Windows: spam_detector_env\Scripts\activate

# Install dependencies in clean environment
pip install --upgrade pip
pip install testresources
pip install -r requirements.txt
```

## 6. Run the Application

```bash
python gmail_spam_detector.py
```

## 7. First-time Authentication

- The browser will open for Gmail authorization
- **You'll see a warning about unverified app - this is normal for testing**
- Click "Advanced" then "Go to Spam Detector (unsafe)"
- Grant the necessary permissions
- The authentication token will be saved for future use

## 8. Troubleshooting OAuth Issues

### If you get "Error 403: access_denied":
1. Make sure you added your email as a test user (Step 3)
2. Try deleting `token.json` and re-authenticating
3. Check that Gmail API is enabled in your project

### If you see "This app isn't verified":
1. This is normal for testing - click "Advanced"
2. Click "Go to [your app name] (unsafe)"
3. For production use, you'd need to submit for verification

### If you get SSL certificate errors:
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### If you get permission errors:
```bash
pip install --user -r requirements.txt
```

### If NLTK data download fails:
```python
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
```

## Usage Examples

```python
# Initialize detector
detector = GmailSpamDetector()

# Train or load model
detector.train_model()  # or detector.load_model()

# Authenticate Gmail
detector.authenticate_gmail()

# Check recent emails
results = detector.check_gmail_spam(max_results=50, days_back=7)

# Check specific text
prediction, confidence = detector.predict_spam("Your text here")
```

## Common Issues and Solutions

1. **OAuth 403 access_denied**: Add your email as test user in OAuth consent screen
2. **App not verified warning**: Normal for testing - click "Advanced" then proceed
3. **Dependency conflicts**: Use virtual environment
4. **Gmail API quota exceeded**: Wait or request quota increase
5. **Authentication issues**: Delete `token.json` and re-authenticate
6. **Model not found**: Run training first or check file paths

## Production Deployment (Optional)

If you want to publish this app for others to use:
1. Submit your app for Google verification
2. This process can take several weeks
3. For personal/testing use, the test user approach is sufficient
