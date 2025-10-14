import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from src.apps.individual import individual_page
from src.util import disclaimer_text


auth_file = '.auth/auth.yaml'
with open(auth_file) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

page_title = "Invest.AI（内测版）"
st.set_page_config(page_title=page_title)
st.subheader(page_title, divider="gray")
individual_page()
st.write(disclaimer_text)
st.write("© 2025 invest-ai.click All rights reserved.")
