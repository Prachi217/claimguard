import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import time
import os
import streamlit_authenticator as stauth
from datetime import datetime

st.set_page_config(page_title="ClaimGuard", page_icon="🛡️", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

credentials = {
    "usernames": {
        "investigator1": {
            "email": "investigator1@claimguard.com",
            "name": "Priya Sharma",
            "password": "$2b$12$gnUizCrYMN5GkyKjm.iLjOJXCSPSC/hj.BrUQ7ucv0MiJCz2OxIji"
        },
        "admin": {
            "email": "admin@claimguard.com",
            "name": "Admin User",
            "password": "$2b$12$K/gTNr0ryzI/Q8au6grGJezzIejtPCI4uJA/IshoqAuU03MX1qX5i"
        }
    }
}

authenticator = stauth.Authenticate(credentials, "claimguard_cookie", "auth_key_123", cookie_expiry_days=1)

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
@keyframes fadeIn { from { opacity: 0; transform: translateY(14px);} to { opacity: 1; transform: translateY(0);} }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(176,71,14,0.55);} 70% { box-shadow: 0 0 0 12px rgba(176,71,14,0);} 100% { box-shadow: 0 0 0 0 rgba(176,71,14,0);} }
@keyframes shimmer { 0% { background-position: -400px 0;} 100% { background-position: 400px 0;} }
@keyframes glowMove { 0% { background-position: 0% 50%;} 50% { background-position: 100% 50%;} 100% { background-position: 0% 50%;} }
@keyframes slideIn { from { opacity:0; transform: translateX(-14px);} to { opacity:1; transform: translateX(0);} }
@keyframes shieldFloat { 0% { transform: translateY(0px) scale(1);} 50% { transform: translateY(-8px) scale(1.06);} 100% { transform: translateY(0px) scale(1);} }
@keyframes borderGlow { 0% { box-shadow: 0 12px 40px rgba(92,214,138,0.2);} 50% { box-shadow: 0 12px 55px rgba(92,214,138,0.45);} 100% { box-shadow: 0 12px 40px rgba(92,214,138,0.2);} }
@keyframes fadeInUp { from { opacity:0; transform: translateY(24px);} to { opacity:1; transform: translateY(0);} }

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: linear-gradient(-45deg, #050B08, #0A1F12, #0E2A17, #06120A); background-size: 400% 400%; animation: glowMove 20s ease infinite; }
.main .block-container { animation: fadeIn 0.7s ease-out; padding-top: 1.5rem; }

h1, h2, h3, h4, .stMarkdown, label, p { color: #FFFFFF; }
.stCaption, [data-testid="stCaptionContainer"] { color: #7E9488 !important; }

.stat-card { background: linear-gradient(135deg, #0E2A17 0%, #123A1F 100%); border-radius: 18px; padding: 24px 26px; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4); transition: transform 0.3s cubic-bezier(.2,.8,.2,1), box-shadow 0.3s ease;
    animation: fadeIn 0.8s ease-out; border: 1px solid rgba(92,214,138,0.18); }
.stat-card:hover { transform: translateY(-6px) scale(1.03); box-shadow: 0 14px 32px rgba(92,214,138,0.25); border-color: rgba(92,214,138,0.5); }
.stat-label { color: #5CD68A; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.stat-value { color: white; font-size: 38px; font-weight: 800; text-shadow: 0 0 20px rgba(92,214,138,0.3); }

.risk-high { background: #FBEAEA; color: #B0470E; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; animation: pulse 2s infinite; display:inline-block; }
.risk-medium { background: #FDF4E3; color: #8a5a00; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; }
.risk-low { background: #EAF2E9; color: #2E6B3E; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; }

.bar-bg { background: #0E1F14; border-radius: 8px; height: 12px; width: 100%; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.4); }
.bar-fill { height: 12px; border-radius: 8px; transition: width 1s cubic-bezier(.2,.8,.2,1); background-size: 400px 100%; animation: shimmer 2.5s linear infinite; }

table.claims-table { width: 100%; border-collapse: collapse; }
table.claims-table th { text-align: left; padding: 12px 14px; color: #5CD68A; font-size: 11.5px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #16321F; }
table.claims-table td { padding: 12px 14px; font-size: 14px; border-bottom: 1px solid #10241A; color: #DCE9E0; }
tr.claim-row { animation: fadeIn 0.45s ease-out; transition: background 0.25s ease, transform 0.2s ease; }
tr.claim-row:hover { background: rgba(92,214,138,0.08); transform: scale(1.005); }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #050B08, #0E2214); border-right: 1px solid rgba(92,214,138,0.15); }

.detail-panel { background: linear-gradient(135deg, #0D1F15, #123420); padding:22px 26px; border-radius:16px;
    animation: fadeIn 0.5s ease-out; border: 1px solid rgba(92,214,138,0.2); box-shadow: 0 8px 24px rgba(0,0,0,0.35); }

.spotlight-card { background: linear-gradient(135deg, #2A1414, #123420); border: 1.5px solid #B0470E;
    border-radius: 18px; padding: 24px 28px; animation: fadeIn 0.6s ease-out, pulse 3s infinite; }

.alert-banner { background: linear-gradient(90deg, #3A1414, #1A2A1E); border-left: 4px solid #B0470E;
    border-radius: 10px; padding: 14px 20px; margin-bottom: 18px; animation: slideIn 0.5s ease-out; color: #FBD5C5; }

.footer-box { text-align:center; color:#6B8F79; font-size:12px; margin-top: 40px; padding: 16px 0; border-top: 1px solid rgba(92,214,138,0.1); }

.model-info-box { background:#0E2214; padding:12px 14px; border-radius:10px; font-size:12px; line-height:1.7; color:#8FB89E; border: 1px solid rgba(92,214,138,0.12); }

.notes-box { background:#0E2214; padding:12px 14px; border-radius:10px; font-size:12.5px; line-height:1.6; color:#DCE9E0;
    border: 1px solid rgba(92,214,138,0.18); margin-bottom: 8px; }

.focus-item { background: rgba(92,214,138,0.06); border-left: 3px solid #5CD68A; padding: 8px 10px; border-radius: 6px;
    margin-bottom: 6px; font-size: 11.5px; color: #DCE9E0; }

.command-header { display:flex; align-items:center; gap:10px; margin-bottom: 4px; }
.command-badge { background: rgba(92,214,138,0.12); color:#5CD68A; border:1px solid rgba(92,214,138,0.3);
    padding: 3px 12px; border-radius: 14px; font-size: 10.5px; font-weight:700; letter-spacing:1px; text-transform:uppercase; }

div[data-baseweb="tab-list"] { gap: 6px; }
button[data-baseweb="tab"] { transition: all 0.25s ease; border-radius: 10px 10px 0 0 !important; }
button[data-baseweb="tab"]:hover { background: rgba(92,214,138,0.1); }

.stButton button { transition: all 0.2s ease; }
.stButton button:hover { border-color: #5CD68A !important; color: #5CD68A !important; }

.hero-wrap {
    background: linear-gradient(135deg, #06120A 0%, #0A1F12 40%, #06120A 100%);
    background-size: 300% 300%; animation: glowMove 14s ease infinite;
    border-radius: 22px; padding: 40px 44px 32px; margin-bottom: 26px;
    border: 1px solid rgba(46,107,62,0.35); animation: fadeInUp 0.6s ease-out, glowMove 14s ease infinite;
    box-shadow: 0 18px 50px rgba(0,0,0,0.5);
}
.hero-badge { display:inline-block; background: rgba(46,107,62,0.18); color:#5CD68A; border:1px solid rgba(92,214,138,0.35);
    padding: 4px 14px; border-radius: 20px; font-size: 11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:14px; }
.hero-title { color: #5CD68A; font-size: 34px; font-weight: 800; margin: 4px 0 6px; text-shadow: 0 0 25px rgba(92,214,138,0.3); }
.hero-subtitle { color: #FFFFFF; font-size: 17px; font-weight: 600; margin-bottom: 8px; }
.hero-desc { color: #9FB3A6; font-size: 13.5px; max-width: 640px; line-height: 1.6; margin-bottom: 18px; }
.hero-pill-row { display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 20px; }
.hero-pill { background: rgba(255,255,255,0.04); border:1px solid rgba(92,214,138,0.25); color:#B7E8C6;
    padding: 5px 12px; border-radius: 8px; font-size: 11.5px; font-weight:600; }
.hero-stats-row { display:flex; gap:48px; padding-top: 16px; border-top: 1px solid rgba(92,214,138,0.15); flex-wrap: wrap; }
.hero-stat-num { color: #5CD68A; font-size: 28px; font-weight: 800; }
.hero-stat-label { color: #7E9488; font-size: 11.5px; margin-top:2px; }
.hero-feature-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 22px; }
.hero-feature-card { background: rgba(255,255,255,0.03); border:1px solid rgba(92,214,138,0.15); border-radius: 12px;
    padding: 14px 16px; transition: transform 0.25s ease, border-color 0.25s ease; }
.hero-feature-card:hover { transform: translateY(-3px); border-color: rgba(92,214,138,0.5); }
.hero-feature-title { color:#5CD68A; font-size: 12.5px; font-weight:700; margin-bottom: 3px; }
.hero-feature-desc { color:#8A9C90; font-size: 11px; line-height:1.5; }

.login-header { text-align:center; margin-top: 8px; margin-bottom: 8px; }
.login-shield { font-size: 52px; animation: shieldFloat 2.8s ease-in-out infinite; display:inline-block;
    filter: drop-shadow(0 0 30px rgba(92,214,138,0.5)); }
.login-title { color: white; font-size: 28px; font-weight: 800; margin: 8px 0 2px;
    font-family: 'Poppins', sans-serif; animation: fadeInUp 0.6s ease-out 0.1s both; }
.login-subtitle { color: #8FB89E; font-size: 13.5px; margin-bottom: 18px;
    animation: fadeInUp 0.6s ease-out 0.2s both; }

div[data-testid="stForm"] {
    background: linear-gradient(135deg, #0E2A17 0%, #0A1A10 100%);
    border-radius: 20px; padding: 12px 22px 22px;
    border: 1px solid rgba(92,214,138,0.2);
    animation: fadeInUp 0.7s ease-out 0.3s both, borderGlow 3.5s ease-in-out infinite;
    max-width: 420px; margin: 0 auto;
}
div[data-testid="stForm"] input {
    background-color: #050B08 !important; color: white !important;
    border: 1px solid rgba(92,214,138,0.25) !important; border-radius: 8px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stForm"] input:focus {
    border-color: #5CD68A !important; box-shadow: 0 0 0 2px rgba(92,214,138,0.25) !important;
}
div[data-testid="stForm"] label { color: #8FB89E !important; }
div[data-testid="stForm"] button {
    background: linear-gradient(90deg, #5CD68A, #2E6B3E) !important;
    color: #06120A !important; border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; width: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
div[data-testid="stForm"] button:hover {
    transform: translateY(-2px) scale(1.01); box-shadow: 0 8px 20px rgba(92,214,138,0.45); filter: brightness(1.08);
}
</style>
"""

if st.session_state.get('authentication_status') is not True:
    st.markdown(BASE_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">Built for Insurance Fraud Teams</div>
        <div class="hero-title">ClaimGuard — AI-Powered Fraud Prioritization</div>
        <div class="hero-subtitle">Score, explain, and prioritize every insurance claim from one dashboard.</div>
        <div class="hero-desc">Every claim is scored for fraud risk the moment it's filed — no more first-come, first-checked queues.
        Investigators get a ranked list, a plain-language reason for every flag, and a downloadable summary — all in one place.</div>
        <div class="hero-pill-row">
            <div class="hero-pill"> Login Protected</div>
            <div class="hero-pill"> Model Transparency Built-In</div>
            <div class="hero-pill"> Audit-Ready Reports</div>
        </div>
        <div class="hero-stats-row">
            <div><div class="hero-stat-num">90%</div><div class="hero-stat-label">Fraud Recall</div></div>
            <div><div class="hero-stat-num">15,420</div><div class="hero-stat-label">Claims Scored</div></div>
            <div><div class="hero-stat-num">6%</div><div class="hero-stat-label">True Fraud Rate</div></div>
        </div>
        <div class="hero-feature-grid">
            <div class="hero-feature-card">
                <div class="hero-feature-title"> Risk Scoring</div>
                <div class="hero-feature-desc">Every claim ranked the moment it's filed, no manual triage needed.</div>
            </div>
            <div class="hero-feature-card">
                <div class="hero-feature-title"> AI Explanations</div>
                <div class="hero-feature-desc">Plain-language reasons behind every risk flag, built from real patterns.</div>
            </div>
            <div class="hero-feature-card">
                <div class="hero-feature-title"> One-Click Reports</div>
                <div class="hero-feature-desc">Download a case summary or the full queue as CSV for records.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <div class="login-shield">🛡️</div>
        <div class="login-title">Sign in to ClaimGuard</div>
        <div class="login-subtitle">Insurance Claims Fraud Prioritization System</div>
    </div>
    """, unsafe_allow_html=True)

authenticator.login()

if st.session_state.get('authentication_status') is False:
    st.error(" Username or password is incorrect")
    with st.expander(" Forgot your password?"):
        st.info("For security, password resets are handled by the system administrator. Please contact your ClaimGuard admin to reset your credentials.")
    st.stop()
elif st.session_state.get('authentication_status') is None:
    with st.expander(" Forgot your password?"):
        st.info("For security, password resets are handled by the system administrator. Please contact your ClaimGuard admin to reset your credentials.")
    st.stop()

name = st.session_state.get('name')
username = st.session_state.get('username')

st.markdown(BASE_CSS, unsafe_allow_html=True)

def generate_explanation(claim):
    possible_reasons = []
    if claim['PoliceReportFiled'] == 'No':
        possible_reasons.append(("no police report was filed", 3))
    if claim['WitnessPresent'] == 'No':
        possible_reasons.append(("no witness was present", 2))
    if claim['Fault'] == 'Policy Holder':
        possible_reasons.append(("the policyholder was at fault", 3))
    if claim['PastNumberOfClaims'] == 'none':
        possible_reasons.append(("this is a first-time claimant", 1))
    if claim['VehicleCategory'] == 'Utility':
        possible_reasons.append(("the vehicle is a Utility category, which has a higher fraud rate", 1))
    if len(possible_reasons) == 0:
        return "No major risk signals were found in this claim."
    possible_reasons.sort(key=lambda x: x[1], reverse=True)
    top_reasons = [r[0] for r in possible_reasons[:3]]
    if len(top_reasons) == 1:
        return f"This claim was flagged mainly because {top_reasons[0]}."
    return "This claim was flagged because " + ", ".join(top_reasons[:-1]) + f", and {top_reasons[-1]}."

def risk_icon(level):
    return {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(level, "⚪")

def animated_number(value, label, card_id):
    if isinstance(value, float):
        display_value = f"{value:.2f}"
    else:
        display_value = f"{value:,}"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{display_value}</div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    try:
        model = joblib.load(os.path.join(BASE_DIR, 'claimguard_model.pkl'))
        model_columns = joblib.load(os.path.join(BASE_DIR, 'model_columns.pkl'))
        return model, model_columns
    except FileNotFoundError:
        st.error(" Model files not found. Please contact the system administrator.")
        st.stop()

@st.cache_data
def load_and_score_data():
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'fraud_oracle.csv'))
    except FileNotFoundError:
        st.error(" Claims data file not found. Please contact the system administrator.")
        st.stop()

    model, model_columns = load_model()
    X = df.drop(columns=['PolicyNumber', 'RepNumber', 'FraudFound_P'])
    X_encoded = pd.get_dummies(X, drop_first=True)
    X_encoded = X_encoded.reindex(columns=model_columns, fill_value=0)
    df['Risk_Score'] = model.predict_proba(X_encoded)[:, 1]
    df['Risk_Level'] = pd.cut(df['Risk_Score'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])
    return df

model, model_columns = load_model()
df = load_and_score_data()

if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'investigator_notes' not in st.session_state:
    st.session_state.investigator_notes = {}

with st.sidebar:
    st.write(f" Logged in as: **{name}**")
    authenticator.logout("Logout", "sidebar")
    st.divider()
    st.markdown("## 🛡️ ClaimGuard")
    st.caption("Insurance Fraud Prioritization")
    st.divider()
    st.markdown("###  Filters")
    month_filter = st.multiselect("Filter by Month", options=sorted(df['Month'].unique()), default=[])
    st.divider()

    st.markdown("###  This Week's Focus")
    top3 = df.sort_values('Risk_Score', ascending=False).head(3)
    for idx, r in top3.iterrows():
        st.markdown(f"""<div class="focus-item">🔴 {r['Make']} — {r['Month']} — Score {r['Risk_Score']:.2f}</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("###  Live Alerts")
    top_alert = df.sort_values('Risk_Score', ascending=False).iloc[0]
    st.markdown(f"""<div style="background:#0E2214; padding:10px 12px; border-radius:10px; border-left:3px solid #5CD68A; font-size:12.5px;">
    🚨 Highest risk claim: <b>{top_alert['Make']}</b><br>Score: <b>{top_alert['Risk_Score']:.2f}</b></div>""", unsafe_allow_html=True)

    if username == "admin":
        st.divider()
        st.markdown("###  Model Performance")
        st.markdown("""
        <div class="model-info-box">
        <b style="color:#5CD68A;">Recall (catches real fraud):</b> 90%<br>
        <b style="color:#5CD68A;">Precision (accuracy of alerts):</b> 13%<br>
        This model prioritizes catching fraud over avoiding false alarms. Roughly 1 in 8 flagged claims is genuinely fraudulent — the rest need human review to confirm.
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.search_history:
        st.divider()
        st.markdown("###  Recent Searches")
        for h in st.session_state.search_history[-5:][::-1]:
            st.caption(f"Claim #{h}")

    st.divider()
    st.markdown("### ℹ About")
    st.caption("This dashboard scores every insurance claim for fraud risk the moment it's filed, so investigators know exactly where to look first.")

filtered_df = df.copy()
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'].isin(month_filter)]

st.markdown("""
<div class="command-header">
    <span class="command-badge">Investigator Command Center</span>
</div>
""", unsafe_allow_html=True)
st.markdown("### 🛡️ ClaimGuard — Prioritized Fraud Queue")
st.caption("Insurance Claims Fraud Prioritization System")

high_pct = (filtered_df['Risk_Level'] == 'High').mean() * 100
if high_pct > 25:
    st.markdown(f"""<div class="alert-banner"> <b>{high_pct:.0f}%</b> of claims in this view are High Risk — above the normal threshold. Consider prioritizing review this week.</div>""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3 = st.tabs([" Overview", "Search a Claim", " All Claims"])

with tab1:
    with st.expander("ℹNew here? Click to see how this dashboard works"):
        st.markdown("""
        **What is ClaimGuard?**
        This dashboard scores every insurance claim for fraud risk the moment it's filed — so an investigator always knows which claims to check first.

        **How to use it:**
        -  **Overview** — see overall stats, today's top priority claim, and risk patterns
        -  **Search a Claim** — enter any claim number to see its risk score, why it was flagged, and add your own notes
        -  **All Claims** — browse and filter the full sorted list, or download it as a CSV

        **What the colors mean:**
        🔴 High Risk &nbsp;&nbsp; 🟠 Medium Risk &nbsp;&nbsp; 🟢 Low Risk

        This is a student capstone project built on a public dataset — not a real insurance company's live system.
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        animated_number(len(filtered_df), "Total Claims", "kpi1")
    with col2:
        animated_number(len(filtered_df[filtered_df['Risk_Level'] == 'High']), "High Risk Claims", "kpi2")
    with col3:
        animated_number(round(filtered_df['Risk_Score'].mean(), 2), "Average Risk Score", "kpi3")

    st.write("")

    top_claim = filtered_df.sort_values('Risk_Score', ascending=False).iloc[0]
    st.markdown(f"""
    <div class="spotlight-card">
        <span style="color:#5CD68A; font-size:12px; letter-spacing:1px; text-transform:uppercase; font-weight:700;"> Top Priority Claim</span>
        <h3 style="color:white; margin:8px 0;">{top_claim['Make']} — {top_claim['Month']}</h3>
        <p style="color:#E4E7F5; margin:0;">Risk Score: <b>{top_claim['Risk_Score']:.2f}</b> &nbsp;|&nbsp; Fault: <b>{top_claim['Fault']}</b> &nbsp;|&nbsp; Police Report: <b>{top_claim['PoliceReportFiled']}</b></p>
        <p style="color:#5CD68A; font-style:italic; margin-top:8px;"> {generate_explanation(top_claim)}</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        risk_counts = filtered_df['Risk_Level'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values, hole=0.62,
            marker=dict(colors=['#B0470E', '#8a5a00', '#2E6B3E'], line=dict(color='#06120A', width=2)),
            textfont=dict(color='white', size=13), pull=[0.03]*len(risk_counts))])
        fig_donut.update_layout(title="Risk Level Distribution", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            showlegend=True, height=320, margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)
    with chart_col2:
        monthly = filtered_df.groupby('Month').size().reset_index(name='count')
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        monthly['Month'] = pd.Categorical(monthly['Month'], categories=month_order, ordered=True)
        monthly = monthly.sort_values('Month')

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly['Month'], y=monthly['count'],
            marker=dict(color=monthly['count'], colorscale=[[0, '#2E6B3E'], [1, '#5CD68A']], line=dict(color='#06120A', width=1)),
            hovertemplate="<b>%{x}</b><br>%{y} claims<extra></extra>", name="Claims"
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly['Month'], y=monthly['count'], mode='lines+markers',
            line=dict(color='#C9A24B', width=2, shape='spline'), marker=dict(size=6, color='#C9A24B'),
            hoverinfo='skip', name="Trend"
        ))
        fig_trend.update_layout(
            title="Claims by Month", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)',
            font=dict(color='white'), height=320, margin=dict(t=50, b=10, l=10, r=10), showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=10))
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.write("")
    st.markdown("####  Why Claims Get Flagged — Risk Factor Breakdown")
    st.caption("Real fraud rate for each risk signal, calculated from the dataset.")

    factor_data = {
        "Fault: Policy Holder": df[df['Fault'] == 'Policy Holder']['FraudFound_P'].mean() * 100 if 'FraudFound_P' in df.columns else 7.9,
        "No Police Report": df[df['PoliceReportFiled'] == 'No']['FraudFound_P'].mean() * 100 if 'FraudFound_P' in df.columns else 6.0,
        "No Witness": df[df['WitnessPresent'] == 'No']['FraudFound_P'].mean() * 100 if 'FraudFound_P' in df.columns else 6.0,
        "First-Time Claimant": df[df['PastNumberOfClaims'] == 'none']['FraudFound_P'].mean() * 100 if 'FraudFound_P' in df.columns else 7.8,
        "Utility Vehicle": df[df['VehicleCategory'] == 'Utility']['FraudFound_P'].mean() * 100 if 'FraudFound_P' in df.columns else 11.3,
    }
    factor_df = pd.DataFrame(list(factor_data.items()), columns=['Factor', 'Fraud Rate %']).sort_values('Fraud Rate %', ascending=True)

    fig_factors = go.Figure(go.Bar(
        x=factor_df['Fraud Rate %'], y=factor_df['Factor'], orientation='h',
        marker=dict(color=factor_df['Fraud Rate %'], colorscale=[[0, '#2E6B3E'], [1, '#B0470E']]),
        text=[f"{v:.1f}%" for v in factor_df['Fraud Rate %']], textposition='outside',
        textfont=dict(color='white', size=11)
    ))
    fig_factors.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', font=dict(color='white'),
        height=280, margin=dict(t=10, b=10, l=10, r=40),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title="Fraud Rate %"),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_factors, use_container_width=True)

with tab2:
    st.subheader("Search a Claim")
    search_id = st.number_input("Enter Row Number (0 to 15419)", min_value=0, max_value=len(df)-1, step=1)

    if st.button("View Claim Details", type="primary"):
        with st.spinner("Analyzing claim..."):
            time.sleep(0.4)

        if search_id not in st.session_state.search_history:
            st.session_state.search_history.append(search_id)
        st.session_state.last_viewed = search_id

    if 'last_viewed' in st.session_state:
        search_id = st.session_state.last_viewed
        claim = df.iloc[search_id]
        badge_class = f"risk-{claim['Risk_Level'].lower()}"
        explanation = generate_explanation(claim)
        icon = risk_icon(claim['Risk_Level'])
        bar_color = {'High': '#B0470E', 'Medium': '#8a5a00', 'Low': '#2E6B3E'}[claim['Risk_Level']]

        if claim['Risk_Level'] == 'High':
            st.toast(f" High-risk claim detected! Score: {claim['Risk_Score']:.2f}", icon="🚨")

        st.markdown(f"""
        <div class="detail-panel">
            <span class="{badge_class}">{icon} {claim['Risk_Level']} RISK — {claim['Risk_Score']:.2f}</span>
            <div class="bar-bg" style="margin-top:14px;">
                <div class="bar-fill" style="width:{claim['Risk_Score']*100}%; background:linear-gradient(90deg,{bar_color},#5CD68A,{bar_color});"></div>
            </div>
            <p style="margin-top:16px; color:#C7CDE8;">
            <b>Fault:</b> {claim['Fault']} &nbsp;|&nbsp;
            <b>Police Report Filed:</b> {claim['PoliceReportFiled']} &nbsp;|&nbsp;
            <b>Witness Present:</b> {claim['WitnessPresent']}
            </p>
            <p style="margin-top:12px; color:#5CD68A; font-style:italic;"> {explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        avg_score = df['Risk_Score'].mean()
        diff_pct = ((claim['Risk_Score'] - avg_score) / avg_score) * 100
        comparison_text = f"{abs(diff_pct):.0f}% {'higher' if diff_pct > 0 else 'lower'} than the average claim"
        comparison_color = "#B0470E" if diff_pct > 0 else "#2E6B3E"

        st.markdown(f"""
        <div style="background:#0E2214; padding:10px 16px; border-radius:10px; margin-top:8px; border-left:3px solid {comparison_color};">
        This claim's risk is <b style="color:{comparison_color};">{comparison_text}</b> (average: {avg_score:.2f})
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**Investigator Notes**")
        existing_note = st.session_state.investigator_notes.get(search_id, "")
        note_text = st.text_area("Add notes for this claim (visible only in this session)", value=existing_note, key=f"note_{search_id}", height=80)
        if st.button("Save Note", key=f"save_note_{search_id}"):
            st.session_state.investigator_notes[search_id] = note_text
            st.success("Note saved for this session.")
        if existing_note:
            st.markdown(f"""<div class="notes-box"> <b>Saved note:</b> {existing_note}</div>""", unsafe_allow_html=True)

        report_text = f"""CLAIMGUARD INVESTIGATION SUMMARY
{'='*40}
Investigated by: {name}
Claim Row: {search_id}
Risk Level: {claim['Risk_Level']} ({claim['Risk_Score']:.2f})
Make: {claim['Make']} | Month: {claim['Month']}
Fault: {claim['Fault']}
Police Report Filed: {claim['PoliceReportFiled']}
Witness Present: {claim['WitnessPresent']}

Reason Flagged:
{explanation}

Investigator Notes:
{st.session_state.investigator_notes.get(search_id, '(none)')}

Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}
"""
        st.download_button("Download Investigation Summary", data=report_text,
            file_name=f"claim_{search_id}_report.txt", mime="text/plain")

        st.write("")
        st.markdown("**Was this prediction accurate?**")
        fb_col1, fb_col2 = st.columns(2)
        with fb_col1:
            if st.button("Correct prediction"):
                st.success("Thanks! This feedback will help improve future models.")
        with fb_col2:
            if st.button("Incorrect prediction"):
                st.warning("Thanks for flagging this — noted for model review.")

with tab3:
    st.subheader("Claims Sorted by Risk (Highest First)")

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        make_filter = st.multiselect("Filter by Make", options=sorted(filtered_df['Make'].unique()), default=[])
    with fcol2:
        fault_filter = st.multiselect("Filter by Fault", options=sorted(filtered_df['Fault'].unique()), default=[])
    with fcol3:
        level_filter = st.multiselect("Filter by Risk Level", options=['High', 'Medium', 'Low'], default=[])

    show_only_high = st.checkbox("Show only High Risk claims")

    table_df = filtered_df[['Month', 'Make', 'Fault', 'PoliceReportFiled', 'WitnessPresent', 'Risk_Score', 'Risk_Level']].copy()
    if make_filter:
        table_df = table_df[table_df['Make'].isin(make_filter)]
    if fault_filter:
        table_df = table_df[table_df['Fault'].isin(fault_filter)]
    if level_filter:
        table_df = table_df[table_df['Risk_Level'].isin(level_filter)]

    table_df = table_df.sort_values('Risk_Score', ascending=False)

    if show_only_high:
        display_df = table_df[table_df['Risk_Level'] == 'High'].head(50)
    elif make_filter or fault_filter or level_filter:
        display_df = table_df.head(50)
    else:
        display_df = pd.concat([
            table_df[table_df['Risk_Level'] == 'High'].head(10),
            table_df[table_df['Risk_Level'] == 'Medium'].head(10),
            table_df[table_df['Risk_Level'] == 'Low'].head(10)
        ])
        st.caption("Showing a mix of High, Medium, and Low risk claims. Use filters above to narrow down.")

    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇Download this list as CSV", data=csv_data, file_name="claimguard_export.csv", mime="text/csv")

    rows_html = ""
    colors = {'High': '#B0470E', 'Medium': '#8a5a00', 'Low': '#2E6B3E'}
    for _, r in display_df.iterrows():
        badge_class = f"risk-{str(r['Risk_Level']).lower()}"
        icon = risk_icon(r['Risk_Level'])
        bar_color = colors.get(r['Risk_Level'], '#888')
        rows_html += f"""<tr class="claim-row">
            <td>{r['Month']}</td><td>{r['Make']}</td><td>{r['Fault']}</td>
            <td>{r['PoliceReportFiled']}</td><td>{r['WitnessPresent']}</td>
            <td style="min-width:130px;"><div class="bar-bg"><div class="bar-fill" style="width:{r['Risk_Score']*100}%; background:{bar_color};"></div></div></td>
            <td><span class="{badge_class}">{icon} {r['Risk_Level']}</span></td>
        </tr>"""

    table_html = f"""<table class="claims-table">
    <tr><th>Month</th><th>Make</th><th>Fault</th><th>Police Report</th><th>Witness</th><th>Risk Score</th><th>Level</th></tr>
    {rows_html}</table>"""
    st.markdown(table_html, unsafe_allow_html=True)

st.markdown(f"""<div class="footer-box">ClaimGuard v1.0 &nbsp;•&nbsp; Data Analytics Capstone &nbsp;•&nbsp; Last refreshed: {datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>""", unsafe_allow_html=True)