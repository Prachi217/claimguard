import streamlit_authenticator as stauth

hashed_password_1 = stauth.Hasher.hash("investigator123")
hashed_password_2 = stauth.Hasher.hash("admin456")

print("Password 1 hash:", hashed_password_1)
print("Password 2 hash:", hashed_password_2)