# Gmail Spam Detector with Counter-Attack

A machine learning-powered spam detection system that integrates with Gmail API to analyze your emails in real-time. Built with scikit-learn Naive Bayes classifier.

**🎯 NEW: Counter-Attack Feature!** Automatically send rickroll emails back to spammers!

## 🔗 Repository

- GitHub(Code): https://github.com/scalliontor/Gmail-spam-or-ham.git
- Canva(Slide): https://www.canva.com/design/DAGu3r1dtG8/na4Na-2YmaCu8Eg56mffbQ/edit?utm_content=DAGu3r1dtG8&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
- Notion(Note): https://www.notion.so/Project-231838f5c281808d97d8c2ffae73e25c?source=copy_link

## 🌟 Features

- **Spam Detection**: Multinomial Naive Bayes classifier with 95%+ accuracy
- **Gmail Integration**: Real-time scanning of your Gmail messages
- **🎯 Counter-Attack**: Send rickroll emails back to spammers!
- **Web Interface**: User-friendly Streamlit dashboard
- **Auto or Manual**: Choose to send counter-attacks automatically or manually

## 🎯 Counter-Attack Modes

1. **Scan Only**: Just detect spam (safe mode)
2. **Prepare Counter-Attacks**: Detect spam and prepare rickroll emails
3. **Auto Counter-Attack**: Automatically send rickroll emails to spammers! 😈

## Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud Platform account (free tier works)

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/scalliontor/Gmail-spam-or-ham.git
cd Gmail-spam-or-ham

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Gmail Credentials

** Important**: The `credentials.json` file is not included in the repository for security reasons. You need to create your own:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "Gmail Spam Detector"

2. **Enable Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search "Gmail API" and click "Enable"

3. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "CREATE CREDENTIALS" > "OAuth client ID"
   - Choose "Desktop application"
   - Download JSON file and rename to `credentials.json`
   - Place it in the project root directory

4. **Configure OAuth Consent Screen**:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type
   - Fill required fields
   - **IMPORTANT**: Add your email as test user in "Test users" section

### 3. Run the Application

#### Option 1: Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
- Includes counter-attack buttons
- Visual spam detection with rickroll options

#### Option 2: Command Line with Counter-Attack
```bash
python gmail_spam_detector.py
```
- Choose from 3 modes including auto counter-attack
- Manual control over each counter-attack

#### Option 3: Demo Mode
```bash
python counter_attack_demo.py
```
- Test the counter-attack email generation
- Safe demo without sending real emails

### Disclaimer

The counter-attack feature is for educational and entertainment purposes. Use responsibly and in accordance with your local laws and email provider's terms of service. The rickroll is harmless fun, but sending unsolicited emails could have legal implications depending on your jurisdiction.

**Use at your own risk and be a responsible digital citizen!** 


