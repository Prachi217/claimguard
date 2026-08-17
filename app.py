import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

st.set_page_config(page_title="ClaimGuard", page_icon="🛡️", layout="wide")

# ===== AI EXPLANATION FUNCTION =====
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

# ===== CUSTOM CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px);} to { opacity: 1; transform: translateY(0);} }
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.main .block-container { animation: fadeIn 0.6s ease-out; padding-top: 1.5rem; }
.stat-card {
    background: linear-gradient(135deg, #1E2761 0%, #27336B 100%);
    border-radius: 16px; padding: 22px 24px; text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    animation: fadeIn 0.7s ease-out;
}
.stat-card:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 28px rgba(201,162,75,0.25); }
.stat-label { color: #C9A24B; font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
.stat-value { color: white; font-size: 34px; font-weight: 700; }
.risk-high { background: #FBEAEA; color: #B0470E; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.risk-medium { background: #FDF4E3; color: #8a5a00; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.risk-low { background: #EAF2E9; color: #2E6B3E; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.bar-bg { background: #1E2540; border-radius: 8px; height: 10px; width: 100%; overflow: hidden; }
.bar-fill { height: 10px; border-radius: 8px; transition: width 0.6s ease; }
table.claims-table { width: 100%; border-collapse: collapse; }
table.claims-table th { text-align: left; padding: 10px 14px; color: #8792AD; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #2A3355; }
table.claims-table td { padding: 10px 14px; font-size: 14px; border-bottom: 1px solid #1E2540; }
tr.claim-row { animation: fadeIn 0.4s ease-out; transition: background 0.2s ease; }
tr.claim-row:hover { background: rgba(201,162,75,0.08); }
section[data-testid="stSidebar"] { background: #12162C; }
</style>
""", unsafe_allow_html=True)

# ===== LOAD MODEL & DATA =====
model = joblib.load('claimguard_model.pkl')
model_columns = joblib.load('model_columns.pkl')
df = pd.read_csv('data/fraud_oracle.csv')

X = df.drop(columns=['PolicyNumber', 'RepNumber', 'FraudFound_P'])
X_encoded = pd.get_dummies(X, drop_first=True)
X_encoded = X_encoded.reindex(columns=model_columns, fill_value=0)
df['Risk_Score'] = model.predict_proba(X_encoded)[:, 1]
df['Risk_Level'] = pd.cut(df['Risk_Score'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 🛡️ ClaimGuard")
    st.caption("Insurance Fraud Prioritization")
    st.divider()
    st.markdown("### Filters")
    month_filter = st.multiselect("Filter by Month", options=sorted(df['Month'].unique()), default=[])
    st.divider()
    st.markdown("### About")
    st.caption("This dashboard scores every insurance claim for fraud risk the moment it's filed, so investigators know exactly where to look first.")

filtered_df = df.copy()
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'].isin(month_filter)]

# ===== HEADER =====
st.markdown("### 🛡️ ClaimGuard — Claims Investigation Dashboard")
st.caption("Insurance Claims Fraud Prioritization System")
st.write("")

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Search a Claim", "📋 All Claims"])

# ---------- TAB 1: OVERVIEW ----------
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Claims</div>
        <div class="stat-value">{len(filtered_df):,}</div></div>""", unsafe_allow_html=True)
    with col2:
        high_count = len(filtered_df[filtered_df['Risk_Level'] == 'High'])
        st.markdown(f"""<div class="stat-card"><div class="stat-label">High Risk Claims</div>
        <div class="stat-value">{high_count:,}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Average Risk Score</div>
        <div class="stat-value">{filtered_df['Risk_Score'].mean():.2f}</div></div>""", unsafe_allow_html=True)

    st.write("")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        risk_counts = filtered_df['Risk_Level'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(
            labels=risk_counts.index, values=risk_counts.values, hole=0.6,
            marker=dict(colors=['#B0470E', '#8a5a00', '#2E6B3E']),
            textfont=dict(color='white', size=13)
        )])
        fig_donut.update_layout(
            title="Risk Level Distribution", paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), showlegend=True, height=320,
            margin=dict(t=50, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        avg_score = filtered_df['Risk_Score'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=avg_score * 100,
            title={'text': "Average Risk Score", 'font': {'color': 'white'}},
            number={'suffix': "%", 'font': {'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': "#C9A24B"},
                'steps': [
                    {'range': [0, 30], 'color': '#2E6B3E'},
                    {'range': [30, 60], 'color': '#8a5a00'},
                    {'range': [60, 100], 'color': '#B0470E'}
                ],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=320,
                                 margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

# ---------- TAB 2: SEARCH ----------
with tab2:
    st.subheader("🔍 Search a Claim")
    search_id = st.number_input("Enter Row Number (0 to 15419)", min_value=0, max_value=len(df)-1, step=1)

    if st.button("View Claim Details", type="primary"):
        claim = df.iloc[search_id]
        badge_class = f"risk-{claim['Risk_Level'].lower()}"
        explanation = generate_explanation(claim)
        icon = risk_icon(claim['Risk_Level'])

        if claim['Risk_Level'] == 'High':
            st.toast(f"⚠️ High-risk claim detected! Score: {claim['Risk_Score']:.2f}", icon="🚨")

        st.markdown(f"""
        <div style="background:#151B33; padding:20px 24px; border-radius:14px; animation: fadeIn 0.4s ease-out;">
            <span class="{badge_class}">{icon} {claim['Risk_Level']} RISK — {claim['Risk_Score']:.2f}</span>
            <div class="bar-bg" style="margin-top:12px;">
                <div class="bar-fill" style="width:{claim['Risk_Score']*100}%; background:{'#B0470E' if claim['Risk_Level']=='High' else '#8a5a00' if claim['Risk_Level']=='Medium' else '#2E6B3E'};"></div>
            </div>
            <p style="margin-top:14px; color:#C7CDE8;">
            <b>Fault:</b> {claim['Fault']} &nbsp;|&nbsp;
            <b>Police Report Filed:</b> {claim['PoliceReportFiled']} &nbsp;|&nbsp;
            <b>Witness Present:</b> {claim['WitnessPresent']}
            </p>
            <p style="margin-top:10px; color:#C9A24B; font-style:italic;">🤖 {explanation}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------- TAB 3: ALL CLAIMS TABLE ----------
with tab3:
    st.subheader("📋 Claims Sorted by Risk (Highest First)")
    show_only_high = st.checkbox("Show only High Risk claims")

    display_df = filtered_df[['Month', 'Make', 'Fault', 'PoliceReportFiled', 'WitnessPresent', 'Risk_Score', 'Risk_Level']]
    display_df = display_df.sort_values('Risk_Score', ascending=False)

    if show_only_high:
        display_df = display_df[display_df['Risk_Level'] == 'High'].head(30)
    else:
        display_df = pd.concat([
            display_df[display_df['Risk_Level'] == 'High'].head(10),
            display_df[display_df['Risk_Level'] == 'Medium'].head(10),
            display_df[display_df['Risk_Level'] == 'Low'].head(10)
        ])
        st.caption("Showing a mix of High, Medium, and Low risk claims. Tick the checkbox above to see only High Risk claims, sorted.")

    rows_html = ""
    colors = {'High': '#B0470E', 'Medium': '#8a5a00', 'Low': '#2E6B3E'}
    for _, r in display_df.iterrows():
        badge_class = f"risk-{str(r['Risk_Level']).lower()}"
        icon = risk_icon(r['Risk_Level'])
        bar_color = colors.get(r['Risk_Level'], '#888')
        rows_html += f"""<tr class="claim-row">
            <td>{r['Month']}</td><td>{r['Make']}</td><td>{r['Fault']}</td>
            <td>{r['PoliceReportFiled']}</td><td>{r['WitnessPresent']}</td>
            <td style="min-width:120px;">
                <div class="bar-bg"><div class="bar-fill" style="width:{r['Risk_Score']*100}%; background:{bar_color};"></div></div>
            </td>
            <td><span class="{badge_class}">{icon} {r['Risk_Level']}</span></td>
        </tr>"""

    table_html = f"""
    <table class="claims-table">
    <tr><th>Month</th><th>Make</th><th>Fault</th><th>Police Report</th><th>Witness</th><th>Risk Score</th><th>Level</th></tr>
    {rows_html}
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)