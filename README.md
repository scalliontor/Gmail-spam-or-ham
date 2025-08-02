# Gmail Spam Detector with Auto Counter-Attack

A machine learning-powered spam detection system that integrates with Gmail API to analyze your emails in real-time and automatically rickroll spammers! Built with scikit-learn Naive Bayes classifier.

**AUTO RICKROLL FEATURE!** Automatically sends rickroll emails back to spammers when detected!

## How It Works

1. **Scan**: Analyzes your recent Gmail messages
2. **Detect**: Identifies spam with high confidence (>70%)
3. **Counter-Attack**: Automatically sends rickroll email to spammer
4. **Report**: Shows you which spammers got rickrolled!

## Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/scalliontor/Gmail-spam-or-ham.git
cd Gmail-spam-or-ham
pip install -r requirements.txt
```

### 2. Setup Gmail API
1. Create Google Cloud project and enable Gmail API
2. Download OAuth credentials as `credentials.json`
3. Add your email as test user in OAuth consent screen

### 3. Run Auto-Rickroll Mode
```bash
streamlit run streamlit_app.py
```
- Click "Scan Gmail for Spam" 
- Watch as spammers get automatically rickrolled! 

### Disclaimer

This tool automatically sends rickroll emails to detected spammers. Use responsibly and in accordance with local laws. The rickroll is harmless fun, but consider the ethical implications of automated email responses.

**Use at your own risk and be a responsible digital citizen!**


