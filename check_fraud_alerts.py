import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import smtplib
from email.mime.text import MIMEText
import os

# Supabase connection (unpause karke wapas active karo pehle)
password = quote_plus(os.environ['Prachi@supabase'])
engine = create_engine(f"postgresql://postgres.xcsjsjwlckcggexqznyr:{password}@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres")

query = 'SELECT * FROM claims_scored WHERE "Risk_Score" > 0.7 ORDER BY "Risk_Score" DESC LIMIT 20;'
high_risk = pd.read_sql(query, engine)

if len(high_risk) > 0:
    body = f"High-risk claims found today:\n\n{high_risk.to_string(index=False)}"

    msg = MIMEText(body)
    msg['Subject'] = 'ClaimGuard — Daily High-Risk Claims Alert'
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ['EMAIL_FROM'], os.environ['EMAIL_APP_PASSWORD'])
        server.send_message(msg)
    print(f"Email sent with {len(high_risk)} high-risk claims")
else:
    print("No high-risk claims found")