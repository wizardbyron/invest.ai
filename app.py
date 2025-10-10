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

page_title = "Invest.AI（演示版）"
st.set_page_config(page_title=page_title)
st.header(page_title)


def login_and_activate():
    try:
        authenticator.login(fields={
            'Form name': '用户登录',
            'Username': '用户名',
            'Password': '密码',
            'Login': '登录'})
        if st.session_state.get('authentication_status') == False:
            st.error('用户名或密码错误')
        with st.expander("受邀用户激活"):
            email, username, name = authenticator.register_user(
                pre_authorized=config['pre-authorized']['emails'],
                fields={'Form name': '受邀用户激活',
                        'First name': '姓',
                        'Last name': '名',
                        'Email': '您的Email',
                        'Username': '用户名',
                        'Password': '密码',
                        'Repeat password': '重输密码',
                        'Password hint': '密码提示',
                        'Captcha': '验证码',
                        'Register': '激活',
                        'Dialog name': 'Verification code',
                        'Code': 'Code', 'Submit': 'Submit',
                        'Error': 'Code is incorrect'})
            if email:
                auth_save()
                st.success(f'用户{name}({username})激活成功')
    except Exception as e:
        st.error(e)


def auth_save():
    with open(auth_file, 'w') as file:
        yaml.dump(config,
                  file,
                  default_flow_style=False,
                  allow_unicode=True)


def reset_password():
    if authenticator.reset_password(
            username=st.session_state.get('username'),
            fields={'Form name': '重置密码',
                    'Current password': '当前密码',
                    'New password': '新密码',
                    'Repeat password': '重新输入新密码',
                    'Reset': '重置密码'}):
        auth_save()
        st.success('密码修改成功')


if st.session_state.get('authentication_status'):
    individual_page()
    with st.sidebar.expander('重置密码'):
        reset_password()
    authenticator.logout(
        location='sidebar',
        button_name='退出系统')
else:
    login_and_activate()

st.write(disclaimer_text)
st.write("© 2025 invest-ai.click All rights reserved.")
