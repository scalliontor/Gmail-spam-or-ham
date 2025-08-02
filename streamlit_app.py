import streamlit as st
import pandas as pd
import os
from gmail_spam_detector import GmailSpamDetector

st.set_page_config(page_title="Gmail Spam Detector", page_icon="📧", layout="wide")

st.markdown("""
<style>
    .big-title { font-size: 3rem; color: #ff6b6b; text-align: center; margin-bottom: 2rem; }
    .success-box { background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 1rem; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def setup_detector():
    detector = GmailSpamDetector()
    
    # Load model
    model_ready = detector.load_model()
    if not model_ready and os.path.exists('2cls_spam_text_cls.csv'):
        detector.train_model()
        detector.save_model()
        model_ready = True
    
    # Connect Gmail
    gmail_ready = False
    if os.path.exists('credentials.json'):
        gmail_ready = detector.authenticate_gmail()
    
    return detector, model_ready, gmail_ready

# Initialize
detector, model_ready, gmail_ready = setup_detector()

# Title
st.markdown('<h1 class="big-title">📧 Gmail Spam Detector</h1>', unsafe_allow_html=True)

# Check basic requirements
if not model_ready:
    st.error("❌ Model not ready! Add '2cls_spam_text_cls.csv' file.")
    st.stop()

if not gmail_ready:
    st.error("❌ Gmail not connected! Add 'credentials.json' file.")
    st.stop()

st.success("✅ Ready!")

# Main interface
st.header("🔍 Scan Gmail")

col1, col2 = st.columns(2)
with col1:
    max_emails = st.slider("Emails to scan", 5, 50, 20)
with col2:
    days_back = st.slider("Days back", 1, 30, 7)

# Scan button
if st.button("🔍 Scan Gmail for Spam", type="primary", use_container_width=True):
    
    with st.spinner("Scanning emails and auto-sending counter-attacks..."):
        results, counter_attacks_sent = detector.scan_gmail_for_spam(max_emails, days_back)
    
    if not results:
        st.info("📭 No emails found")
    else:
        # Show summary
        spam_count = sum(1 for r in results if r['is_spam'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📧 Total", len(results))
        with col2:
            st.metric("🚨 Spam", spam_count)
        with col3:
            st.metric("✅ Safe", len(results) - spam_count)
        with col4:
            st.metric("🎯 Rickrolls Sent", counter_attacks_sent)
        
        # Show counter-attack success
        if counter_attacks_sent > 0:
            st.success(f"🎉 Successfully rickrolled {counter_attacks_sent} spammer(s)!")
            st.balloons()
        
        # Show spam if found
        if spam_count > 0:
            st.subheader("🚨 Spam Messages")
            
            # Show spam details
            for i, msg in enumerate([r for r in results if r['is_spam']], 1):
                counter_status = "🎯 Rickrolled!" if msg.get('counter_attack_sent') else "❌ Not sent"
                
                with st.expander(f"🚨 Spam {i}: {msg['subject'][:50]}... | {counter_status}"):
                    st.write(f"From: {msg['sender']}")
                    st.write(f"Confidence: {msg['confidence']:.1%}")
                    if msg.get('counter_attack_sent'):
                        st.write("🎯 **Counter-attack sent successfully!**")
        
        else:
            st.markdown("""
            <div class="success-box">
                <h3>🎉 No Spam!</h3>
                <p>All emails look safe.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Results table
        st.subheader("📋 Results")
        df = pd.DataFrame([{
            'Subject': r['subject'][:50] + '...' if len(r['subject']) > 50 else r['subject'],
            'Status': '🚨 SPAM' if r['is_spam'] else '✅ SAFE',
            'Confidence': f"{r['confidence']:.1%}",
            'Counter-Attack': '🎯 Sent' if r.get('counter_attack_sent') else ('❌ Failed' if r['is_spam'] else '-')
        } for r in results])
        
        st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    📧 Gmail Spam Detector | Built with 🤖 AI<br>
    <small>🎯 Rickrolling spammers since 2024 😈</small>
</div>
""", unsafe_allow_html=True)
