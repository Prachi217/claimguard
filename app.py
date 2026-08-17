import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="ClaimGuard", page_icon="🛡️", layout="wide")

# ===== AI EXPLANATION FUNCTION =====
def generate_explanation(claim):
    # Har reason ke saath uski "strength" (kitna bada risk factor hai)
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
    if claim['AgeOfPolicyHolder'] in ['16 to 17', '18 to 20', '21 to 25']:
        possible_reasons.append(("the policyholder is relatively young", 1))

    if len(possible_reasons) == 0:
        return "No major risk signals were found in this claim."

    # Sabse strong reasons pehle, sirf top 2-3 dikhao
    possible_reasons.sort(key=lambda x: x[1], reverse=True)
    top_reasons = [r[0] for r in possible_reasons[:3]]

    if len(top_reasons) == 1:
        return f"This claim was flagged mainly because {top_reasons[0]}."
    else:
        return "This claim was flagged because " + ", ".join(top_reasons[:-1]) + f", and {top_reasons[-1]}."

# ===== CUSTOM CSS — Styling + Animations =====
st.markdown("""
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.main .block-container {
    animation: fadeIn 0.6s ease-out;
    padding-top: 2rem;
}
.stat-card {
    background: linear-gradient(135deg, #1E2761 0%, #27336B 100%);
    border-radius: 14px;
    padding: 22px 24px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    animation: fadeIn 0.7s ease-out;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 26px rgba(0,0,0,0.5);
}
.stat-label {
    color: #C9A24B;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.stat-value {
    color: white;
    font-size: 34px;
    font-weight: 700;
}
.risk-high { background: #FBEAEA; color: #B0470E; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.risk-medium { background: #FDF4E3; color: #8a5a00; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.risk-low { background: #EAF2E9; color: #2E6B3E; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 12.5px; }
.claim-row {
    animation: fadeIn 0.4s ease-out;
    transition: background 0.2s ease;
}
.claim-row:hover { background: rgba(201,162,75,0.08); }
table.claims-table { width: 100%; border-collapse: collapse; }
table.claims-table th {
    text-align: left; padding: 10px 14px; color: #8792AD;
    font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;
    border-bottom: 1px solid #2A3355;
}
table.claims-table td {
    padding: 10px 14px; font-size: 14px; border-bottom: 1px solid #1E2540;
}
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

# ===== HEADER =====
st.markdown("### 🛡️ ClaimGuard — Claims Investigation Dashboard")
st.caption("Insurance Claims Fraud Prioritization System")
st.write("")

# ===== STAT CARDS =====
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Claims</div>
    <div class="stat-value">{len(df):,}</div></div>""", unsafe_allow_html=True)
with col2:
    high_count = len(df[df['Risk_Level'] == 'High'])
    st.markdown(f"""<div class="stat-card"><div class="stat-label">High Risk Claims</div>
    <div class="stat-value">{high_count:,}</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="stat-card"><div class="stat-label">Average Risk Score</div>
    <div class="stat-value">{df['Risk_Score'].mean():.2f}</div></div>""", unsafe_allow_html=True)

st.write("")
st.divider()

# ===== SEARCH =====
st.subheader("🔍 Search a Claim")
search_id = st.number_input("Enter Row Number (0 to 15419)", min_value=0, max_value=len(df)-1, step=1)

if st.button("View Claim Details"):
    claim = df.iloc[search_id]
    badge_class = f"risk-{claim['Risk_Level'].lower()}"
    explanation = generate_explanation(claim)
    st.markdown(f"""
    <div style="background:#151B33; padding:18px 22px; border-radius:12px; animation: fadeIn 0.4s ease-out;">
        <span class="{badge_class}">{claim['Risk_Level']} RISK — {claim['Risk_Score']:.2f}</span>
        <p style="margin-top:12px; color:#C7CDE8;">
        <b>Fault:</b> {claim['Fault']} &nbsp;|&nbsp;
        <b>Police Report Filed:</b> {claim['PoliceReportFiled']} &nbsp;|&nbsp;
        <b>Witness Present:</b> {claim['WitnessPresent']}
        </p>
        <p style="margin-top:10px; color:#C9A24B; font-style:italic;">🤖 {explanation}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.divider()

# ===== SORTED CLAIMS TABLE (custom HTML with badges) =====
st.subheader("📋 Claims Sorted by Risk (Highest First)")
show_only_high = st.checkbox("Show only High Risk claims")

display_df = df[['Month', 'Make', 'Fault', 'PoliceReportFiled', 'WitnessPresent', 'Risk_Score', 'Risk_Level']]
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
for _, r in display_df.iterrows():
    badge_class = f"risk-{str(r['Risk_Level']).lower()}"
    rows_html += f"""<tr class="claim-row">
        <td>{r['Month']}</td><td>{r['Make']}</td><td>{r['Fault']}</td>
        <td>{r['PoliceReportFiled']}</td><td>{r['WitnessPresent']}</td>
        <td>{r['Risk_Score']:.3f}</td><td><span class="{badge_class}">{r['Risk_Level']}</span></td>
    </tr>"""

table_html = f"""
<table class="claims-table">
<tr><th>Month</th><th>Make</th><th>Fault</th><th>Police Report</th><th>Witness</th><th>Risk Score</th><th>Level</th></tr>
{rows_html}
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)