import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Download NLTK data if not already present
@st.cache_data
def download_nltk_data():
    try:
        import nltk
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        return True
    except:
        return False

# Import the Gmail Spam Detector class
try:
    from gmail_spam_detector import GmailSpamDetector
except ImportError:
    st.error("Could not import GmailSpamDetector. Make sure gmail_spam_detector.py is in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Gmail Spam Checker",
    page_icon="📧",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-success {
        background-color: #e6ffe6;
        border: 2px solid #44ff44;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .status-error {
        background-color: #ffe6e6;
        border: 2px solid #ff4444;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Auto-initialize everything
@st.cache_resource
def initialize_detector():
    download_nltk_data()
    detector = GmailSpamDetector()
    
    # Try to load existing model, if not found, train new one
    if not detector.load_model():
        if os.path.exists('2cls_spam_text_cls.csv'):
            detector.train_model()
            detector.save_model()
        else:
            return detector, False, False
    
    # Auto-authenticate Gmail if credentials exist
    gmail_authenticated = False
    if os.path.exists('credentials.json'):
        try:
            gmail_authenticated = detector.authenticate_gmail()
        except:
            pass
    
    return detector, True, gmail_authenticated

# Initialize detector
with st.spinner("🚀 Initializing Gmail Spam Detector..."):
    detector, model_ready, gmail_ready = initialize_detector()

# Main title
st.markdown('<h1 class="main-header">📧 Gmail Spam Checker</h1>', unsafe_allow_html=True)

# Check if everything is ready
if not model_ready:
    st.error("❌ Dataset file '2cls_spam_text_cls.csv' not found! Please add the dataset to continue.")
    st.stop()

if not gmail_ready:
    if not os.path.exists('credentials.json'):
        st.error("❌ Gmail credentials not found!")
        st.markdown("""
        **Setup Instructions:**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create OAuth 2.0 credentials for desktop application
        3. Download and rename to `credentials.json`
        4. Add your email as test user in OAuth consent screen
        5. Restart this app
        """)
    else:
        st.error("❌ Gmail authentication failed! Check your OAuth setup.")
    st.stop()

# Gmail Scanner Interface
st.markdown("---")
st.success("✅ Everything is ready! Gmail authenticated and model loaded.")

st.header("📧 Gmail Spam Scanner")

# Scanner configuration
col1, col2 = st.columns(2)

with col1:
    max_results = st.slider("Number of emails to scan:", 5, 50, 20)

with col2:
    days_back = st.slider("Days back to scan:", 1, 30, 7)

# Scan button
if st.button("🔍 Scan Gmail for Spam", type="primary", use_container_width=True):
    with st.spinner(f"Scanning {max_results} emails from the last {days_back} days..."):
        try:
            results = detector.check_gmail_spam(max_results, days_back)
            
            if results:
                # Summary metrics
                spam_count = sum(1 for r in results if r['is_spam'])
                ham_count = len(results) - spam_count
                spam_percentage = (spam_count / len(results)) * 100
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📧 Total Emails", len(results))
                with col2:
                    st.metric("🚨 Spam Detected", spam_count)
                with col3:
                    st.metric("✅ Ham (Safe)", ham_count)
                with col4:
                    st.metric("📊 Spam Rate", f"{spam_percentage:.1f}%")
                
                st.markdown("---")
                
                # Show results
                if spam_count > 0:
                    st.subheader("🚨 Spam Messages Found")
                    spam_messages = [r for r in results if r['is_spam']]
                    
                    for i, msg in enumerate(spam_messages, 1):
                        with st.expander(f"Spam {i}: {msg['subject'][:60]}..." if len(msg['subject']) > 60 else f"Spam {i}: {msg['subject']}"):
                            st.write(f"**From:** {msg['sender']}")
                            st.write(f"**Subject:** {msg['subject']}")
                            st.write(f"**Confidence:** {msg['confidence']:.3f}")
                            st.write(f"**Message ID:** {msg['message_id']}")
                else:
                    st.markdown("""
                    <div class="status-success">
                        <h3>🎉 No Spam Found!</h3>
                        <p>All your recent emails look safe.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show all results table
                st.subheader("📋 All Results")
                df_results = pd.DataFrame(results)
                
                # Color code the dataframe
                def highlight_spam(row):
                    if row['prediction'] == 'spam':
                        return ['background-color: #ffe6e6'] * len(row)
                    else:
                        return ['background-color: #e6ffe6'] * len(row)
                
                styled_df = df_results[['subject', 'sender', 'prediction', 'confidence']].style.apply(highlight_spam, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
            else:
                st.info("No emails found in the specified time range.")
                
        except Exception as e:
            st.error(f"❌ Error scanning Gmail: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    📧 Gmail Spam Checker | Built with Streamlit & Gmail API
</div>
""", unsafe_allow_html=True)
