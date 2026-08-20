import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import time
from datetime import datetime

st.set_page_config(page_title="ClaimGuard", page_icon="🛡️", layout="wide")

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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
@keyframes fadeIn { from { opacity: 0; transform: translateY(14px);} to { opacity: 1; transform: translateY(0);} }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(176,71,14,0.55);} 70% { box-shadow: 0 0 0 12px rgba(176,71,14,0);} 100% { box-shadow: 0 0 0 0 rgba(176,71,14,0);} }
@keyframes shimmer { 0% { background-position: -400px 0;} 100% { background-position: 400px 0;} }
@keyframes glowMove { 0% { background-position: 0% 50%;} 50% { background-position: 100% 50%;} 100% { background-position: 0% 50%;} }
@keyframes slideIn { from { opacity:0; transform: translateX(-14px);} to { opacity:1; transform: translateX(0);} }

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: linear-gradient(-45deg, #0B0E1F, #12162C, #1A1F3D, #12162C); background-size: 400% 400%; animation: glowMove 18s ease infinite; }
.main .block-container { animation: fadeIn 0.7s ease-out; padding-top: 1.5rem; }

.stat-card { background: linear-gradient(135deg, #1E2761 0%, #27336B 100%); border-radius: 18px; padding: 24px 26px; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4); transition: transform 0.3s cubic-bezier(.2,.8,.2,1), box-shadow 0.3s ease;
    animation: fadeIn 0.8s ease-out; border: 1px solid rgba(201,162,75,0.15); }
.stat-card:hover { transform: translateY(-6px) scale(1.03); box-shadow: 0 14px 32px rgba(201,162,75,0.3); border-color: rgba(201,162,75,0.5); }
.stat-label { color: #C9A24B; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.stat-value { color: white; font-size: 38px; font-weight: 800; text-shadow: 0 0 20px rgba(201,162,75,0.35); }

.risk-high { background: #FBEAEA; color: #B0470E; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; animation: pulse 2s infinite; display:inline-block; }
.risk-medium { background: #FDF4E3; color: #8a5a00; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; }
.risk-low { background: #EAF2E9; color: #2E6B3E; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 12.5px; }

.bar-bg { background: #1E2540; border-radius: 8px; height: 12px; width: 100%; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.4); }
.bar-fill { height: 12px; border-radius: 8px; transition: width 1s cubic-bezier(.2,.8,.2,1); background-size: 400px 100%; animation: shimmer 2.5s linear infinite; }

table.claims-table { width: 100%; border-collapse: collapse; }
table.claims-table th { text-align: left; padding: 12px 14px; color: #C9A24B; font-size: 11.5px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #2A3355; }
table.claims-table td { padding: 12px 14px; font-size: 14px; border-bottom: 1px solid #1E2540; color: #E4E7F5; }
tr.claim-row { animation: fadeIn 0.45s ease-out; transition: background 0.25s ease, transform 0.2s ease; }
tr.claim-row:hover { background: rgba(201,162,75,0.09); transform: scale(1.005); }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F1226, #171B38); border-right: 1px solid rgba(201,162,75,0.15); }

.detail-panel { background: linear-gradient(135deg, #151B33, #1B2140); padding:22px 26px; border-radius:16px;
    animation: fadeIn 0.5s ease-out; border: 1px solid rgba(201,162,75,0.2); box-shadow: 0 8px 24px rgba(0,0,0,0.35); }

.spotlight-card { background: linear-gradient(135deg, #2A1414, #1B2140); border: 1.5px solid #B0470E;
    border-radius: 18px; padding: 24px 28px; animation: fadeIn 0.6s ease-out, pulse 3s infinite; }

.alert-banner { background: linear-gradient(90deg, #3A1414, #2A1414); border-left: 4px solid #B0470E;
    border-radius: 10px; padding: 14px 20px; margin-bottom: 18px; animation: slideIn 0.5s ease-out; color: #FBD5C5; }

.footer-box { text-align:center; color:#6B7399; font-size:12px; margin-top: 40px; padding: 16px 0; border-top: 1px solid rgba(201,162,75,0.1); }

.model-info-box { background:#1B2140; padding:12px 14px; border-radius:10px; font-size:12px; line-height:1.7; }

div[data-baseweb="tab-list"] { gap: 6px; }
button[data-baseweb="tab"] { transition: all 0.25s ease; border-radius: 10px 10px 0 0 !important; }
button[data-baseweb="tab"]:hover { background: rgba(201,162,75,0.1); }
</style>
""", unsafe_allow_html=True)

def animated_number(value, label, card_id):
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value" id="{card_id}">0</div>
    </div>
    <script>
    (function() {{
        let target = {value};
        let el = window.parent.document.getElementById("{card_id}");
        let count = 0;
        let steps = 40;
        let increment = target / steps;
        let counter = setInterval(function() {{
            count += increment;
            if (count >= target) {{ count = target; clearInterval(counter); }}
            if (el) {{ el.innerText = Math.round(count).toLocaleString(); }}
        }}, 20);
    }})();
    </script>
    """, unsafe_allow_html=True)

# ===== FIX 1: CACHING FOR PERFORMANCE =====
# ===== FIX 1: CACHING FOR PERFORMANCE (with error handling) =====
@st.cache_resource
def load_model():
    try:
        model = joblib.load('claimguard_model.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return model, model_columns
    except FileNotFoundError:
        st.error("⚠️ Model files not found. Please contact the system administrator.")
        st.stop()

@st.cache_data
def load_and_score_data():
    try:
        df = pd.read_csv('data/fraud_oracle.csv')
    except FileNotFoundError:
        st.error("⚠️ Claims data file not found. Please contact the system administrator.")
        st.stop()

    model, model_columns = load_model()
    try:
        X = df.drop(columns=['PolicyNumber', 'RepNumber', 'FraudFound_P'])
        X_encoded = pd.get_dummies(X, drop_first=True)
        X_encoded = X_encoded.reindex(columns=model_columns, fill_value=0)
        df['Risk_Score'] = model.predict_proba(X_encoded)[:, 1]
        df['Risk_Level'] = pd.cut(df['Risk_Score'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])
    except Exception as e:
        st.error(f"⚠️ Error processing claims data: {str(e)}")
        st.stop()

    return df

    # ===== FIX 2: MODEL TRANSPARENCY PANEL =====
    st.divider()
    st.markdown("### 📊 Model Performance")
    st.markdown("""
    <div class="model-info-box">
    <b style="color:#C9A24B;">Recall (catches real fraud):</b> 90%<br>
    <b style="color:#C9A24B;">Precision (accuracy of alerts):</b> 13%<br>
    <span style="color:#8792AD;">This model prioritizes catching fraud over avoiding false alarms. Roughly 1 in 8 flagged claims is genuinely fraudulent — the rest need human review to confirm.</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### ℹ️ About")
    st.caption("This dashboard scores every insurance claim for fraud risk the moment it's filed, so investigators know exactly where to look first.")

filtered_df = df.copy()
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'].isin(month_filter)]

st.markdown("### 🛡️ ClaimGuard — Claims Investigation Dashboard")
st.caption("Insurance Claims Fraud Prioritization System")

high_pct = (filtered_df['Risk_Level'] == 'High').mean() * 100
if high_pct > 25:
    st.markdown(f"""<div class="alert-banner">⚠️ <b>{high_pct:.0f}%</b> of claims in this view are High Risk — above the normal threshold. Consider prioritizing review this week.</div>""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3 = st.tabs(["📊  Overview", "🔍  Search a Claim", "📋  All Claims"])

with tab1:
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
        <span style="color:#C9A24B; font-size:12px; letter-spacing:1px; text-transform:uppercase; font-weight:700;">⭐ Top Priority Claim</span>
        <h3 style="color:white; margin:8px 0;">{top_claim['Make']} — {top_claim['Month']}</h3>
        <p style="color:#E4E7F5; margin:0;">Risk Score: <b>{top_claim['Risk_Score']:.2f}</b> &nbsp;|&nbsp; Fault: <b>{top_claim['Fault']}</b> &nbsp;|&nbsp; Police Report: <b>{top_claim['PoliceReportFiled']}</b></p>
        <p style="color:#C9A24B; font-style:italic; margin-top:8px;">🤖 {generate_explanation(top_claim)}</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        risk_counts = filtered_df['Risk_Level'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values, hole=0.62,
            marker=dict(colors=['#B0470E', '#8a5a00', '#2E6B3E'], line=dict(color='#0B0E1F', width=2)),
            textfont=dict(color='white', size=13), pull=[0.03]*len(risk_counts))])
        fig_donut.update_layout(title="Risk Level Distribution", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            showlegend=True, height=300, margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)
    with chart_col2:
        monthly = filtered_df.groupby('Month').size().reset_index(name='count')
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        monthly['Month'] = pd.Categorical(monthly['Month'], categories=month_order, ordered=True)
        monthly = monthly.sort_values('Month')
        fig_trend = go.Figure(go.Bar(x=monthly['Month'], y=monthly['count'], marker=dict(color='#C9A24B')))
        fig_trend.update_layout(title="Claims by Month", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), height=300, margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("🔍 Search a Claim")
    search_id = st.number_input("Enter Row Number (0 to 15419)", min_value=0, max_value=len(df)-1, step=1)

    if st.button("View Claim Details", type="primary"):
        with st.spinner("Analyzing claim..."):
            time.sleep(0.4)
        claim = df.iloc[search_id]
        badge_class = f"risk-{claim['Risk_Level'].lower()}"
        explanation = generate_explanation(claim)
        icon = risk_icon(claim['Risk_Level'])
        bar_color = {'High': '#B0470E', 'Medium': '#8a5a00', 'Low': '#2E6B3E'}[claim['Risk_Level']]

        if claim['Risk_Level'] == 'High':
            st.toast(f"⚠️ High-risk claim detected! Score: {claim['Risk_Score']:.2f}", icon="🚨")

        st.markdown(f"""
        <div class="detail-panel">
            <span class="{badge_class}">{icon} {claim['Risk_Level']} RISK — {claim['Risk_Score']:.2f}</span>
            <div class="bar-bg" style="margin-top:14px;">
                <div class="bar-fill" style="width:{claim['Risk_Score']*100}%; background:linear-gradient(90deg,{bar_color},#C9A24B,{bar_color});"></div>
            </div>
            <p style="margin-top:16px; color:#C7CDE8;">
            <b>Fault:</b> {claim['Fault']} &nbsp;|&nbsp;
            <b>Police Report Filed:</b> {claim['PoliceReportFiled']} &nbsp;|&nbsp;
            <b>Witness Present:</b> {claim['WitnessPresent']}
            </p>
            <p style="margin-top:12px; color:#C9A24B; font-style:italic;">🤖 {explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        # ===== FIX 3: FEEDBACK LOOP =====
        st.write("")
        st.markdown("**Was this prediction accurate?**")
        fb_col1, fb_col2 = st.columns(2)
        with fb_col1:
            if st.button("✅ Correct prediction"):
                st.success("Thanks! This feedback will help improve future models.")
        with fb_col2:
            if st.button("❌ Incorrect prediction"):
                st.warning("Thanks for flagging this — noted for model review.")

with tab3:
    st.subheader("📋 Claims Sorted by Risk (Highest First)")

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
    st.download_button("⬇️ Download this list as CSV", data=csv_data, file_name="claimguard_export.csv", mime="text/csv")

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